import os
import io
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, send_file, current_app
from flask_login import login_required, current_user
from models import db, QuotationRequest, Quotation, Order, Invoice, Notification, User, CustomerProfile, DealerProfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

portal_bp = Blueprint('portal', __name__)

@portal_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_staff:
        return redirect(url_for('internal.dashboard'))

    requests_query = QuotationRequest.query.filter_by(user_id=current_user.id)
    total_requests = requests_query.count()
    pending_requests = requests_query.filter(QuotationRequest.status.in_(['Pending Sales Review', 'Under Technical Review', 'Quotation Under Preparation'])).count()

    quotations_query = Quotation.query.filter_by(user_id=current_user.id)
    total_quotations = quotations_query.count()
    active_quotations = quotations_query.filter_by(status='Sent').count()

    orders_query = Order.query.filter_by(user_id=current_user.id)
    total_orders = orders_query.count()
    active_orders = orders_query.filter(Order.status != 'Delivered').count()

    recent_requests = requests_query.order_by(QuotationRequest.created_at.desc()).limit(5).all()
    recent_quotations = quotations_query.order_by(Quotation.created_at.desc()).limit(5).all()
    recent_orders = orders_query.order_by(Order.created_at.desc()).limit(5).all()
    recent_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    invoices_count = Invoice.query.filter_by(user_id=current_user.id).count()

    stats = {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'total_quotations': total_quotations,
        'active_quotations': active_quotations,
        'total_orders': total_orders,
        'active_orders': active_orders
    }

    counts = {
        'rfqs': total_requests,
        'quotations': total_quotations,
        'orders': total_orders,
        'invoices': invoices_count
    }

    return render_template(
        'portal/dashboard.html',
        stats=stats,
        counts=counts,
        recent_requests=recent_requests,
        recent_quotations=recent_quotations,
        recent_orders=recent_orders,
        recent_notifications=recent_notifications
    )

@portal_bp.route('/my-requests')
@login_required
def my_requests():
    requests = QuotationRequest.query.filter_by(user_id=current_user.id).order_by(QuotationRequest.created_at.desc()).all()
    return render_template('portal/requests.html', requests=requests)

@portal_bp.route('/my-requests/<request_number>')
@login_required
def request_detail(request_number):
    rfq = QuotationRequest.query.filter_by(request_number=request_number).first_or_404()
    if rfq.user_id != current_user.id and not current_user.is_staff:
        abort(403)
    return render_template('portal/request_detail.html', rfq=rfq)

@portal_bp.route('/my-quotations')
@login_required
def my_quotations():
    quotations = Quotation.query.filter_by(user_id=current_user.id).order_by(Quotation.created_at.desc()).all()
    return render_template('portal/quotations.html', quotations=quotations)

@portal_bp.route('/my-quotations/<quotation_number>')
@login_required
def quotation_detail(quotation_number):
    quote = Quotation.query.filter_by(quotation_number=quotation_number).first_or_404()
    if quote.user_id != current_user.id and not current_user.is_staff:
        abort(403)
    return render_template('portal/quotation_detail.html', quote=quote, quotation=quote)

@portal_bp.route('/my-quotations/<quotation_number>/accept', methods=['POST'])
@login_required
def accept_quotation(quotation_number):
    quote = Quotation.query.filter_by(quotation_number=quotation_number).first_or_404()
    if quote.user_id != current_user.id:
        abort(403)
    if quote.status not in ('Sent', 'Issued'):
        flash('This quotation cannot be accepted in its current status.', 'warning')
        return redirect(url_for('portal.quotation_detail', quotation_number=quotation_number))

    po_number = request.form.get('po_number', '').strip()
    quote.status = 'Accepted'
    quote.customer_notes = po_number or request.form.get('notes', 'Accepted by customer')

    # Create official confirmed order
    date_str = datetime.now().strftime('%Y%m%d')
    prefix = f'GPT-ORD-{date_str}-'
    latest_order = Order.query.filter(Order.order_number.like(f'{prefix}%')).order_by(Order.id.desc()).first()
    seq = (int(latest_order.order_number.split('-')[-1]) + 1) if latest_order else 1
    order_number = f'{prefix}{seq:03d}'

    order = Order(
        order_number=order_number,
        quotation_id=quote.id,
        user_id=current_user.id,
        status='Order Confirmed',
        transformer_model=quote.request.suggested_transformer or 'Automatic Servo Stabilizer / VCB Panel',
        capacity=quote.request.selected_capacity,
        total_amount=quote.total_amount,
        tracking_reference=po_number or 'Confirmed',
        estimated_delivery=(datetime.now() + timedelta(days=21)).strftime('%d %B %Y')
    )
    db.session.add(order)

    # Customer notification
    notif = Notification(
        user_id=current_user.id,
        title=f'Order Confirmed: {order_number}',
        message=f'Your order {order_number} for {quote.request.selected_capacity} equipment has been confirmed and scheduled for production.',
        type='success',
        link_url=f'/my-orders'
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Quotation {quotation_number} accepted! Order {order_number} has been created and scheduled for production.', 'success')
    return redirect(url_for('portal.my_orders'))

@portal_bp.route('/my-quotations/<quotation_number>/revision', methods=['POST'], endpoint='request_revision')
@portal_bp.route('/my-quotations/<quotation_number>/request-revision', methods=['POST'], endpoint='request_quotation_revision')
@login_required
def request_revision(quotation_number):
    quote = Quotation.query.filter_by(quotation_number=quotation_number).first_or_404()
    if quote.user_id != current_user.id:
        abort(403)

    notes = request.form.get('notes', '').strip()
    if not notes:
        flash('Please provide comments for the requested quotation revision.', 'error')
        return redirect(url_for('portal.quotation_detail', quotation_number=quotation_number))

    quote.status = 'Revision Requested'
    quote.customer_notes = notes

    # Notify customer
    notif = Notification(
        user_id=current_user.id,
        title=f'Revision Requested for {quotation_number}',
        message='Your revision request has been forwarded to the Gauri Power Sales Department.',
        type='info',
        link_url=f'/my-quotations/{quotation_number}'
    )
    db.session.add(notif)
    db.session.commit()

    flash('Revision request sent to the Sales Department.', 'info')
    return redirect(url_for('portal.quotation_detail', quotation_number=quotation_number))

@portal_bp.route('/my-quotations/<quotation_number>/decline', methods=['POST'])
@login_required
def decline_quotation(quotation_number):
    quote = Quotation.query.filter_by(quotation_number=quotation_number).first_or_404()
    if quote.user_id != current_user.id:
        abort(403)

    quote.status = 'Declined'
    quote.customer_notes = request.form.get('notes', 'Declined by customer')
    db.session.commit()

    flash('Quotation marked as declined.', 'info')
    return redirect(url_for('portal.quotation_detail', quotation_number=quotation_number))

@portal_bp.route('/my-quotations/<quotation_number>/pdf')
@login_required
def download_quotation_pdf(quotation_number):
    quote = Quotation.query.filter_by(quotation_number=quotation_number).first_or_404()
    if quote.user_id != current_user.id and not current_user.is_staff:
        abort(403)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0B192C'),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        alignment=1
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0B192C'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )

    elements.append(Paragraph('GAURI POWER', title_style))
    elements.append(Paragraph('Vill. Nanakpura, Opp J.J. Valley, Ropar - 140001 (Punjab) | MD: +91-81789-80216 | Technical Head: +91-78149-43673 | Email: Gauripower09@gmail.com', subtitle_style))
    elements.append(Spacer(1, 15))

    header_data = [
        [Paragraph(f'<b>OFFICIAL COMMERCIAL QUOTATION</b><br/>Ref: {quote.quotation_number}', body_style),
         Paragraph(f'<b>Date:</b> {quote.created_at.strftime("%d %b %Y")}<br/><b>Valid Until:</b> {quote.valid_until.strftime("%d %b %Y")}', body_style)],
        [Paragraph(f'<b>Customer / Client:</b><br/>{quote.request.customer_name}<br/>{quote.request.company_name}<br/>{quote.request.address_line}, {quote.request.city}', body_style),
         Paragraph(f'<b>Associated RFQ:</b> {quote.request.request_number}<br/><b>Contact:</b> {quote.request.contact_number}<br/><b>Email:</b> {quote.request.email}', body_style)]
    ]
    t_header = Table(header_data, colWidths=[270, 270])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph('TECHNICAL SPECIFICATION', h2_style))
    tech_data = [
        ['Parameter', 'Specification Details'],
        ['Equipment / Model', quote.request.suggested_transformer or 'Automatic Voltage Controller / VCB Panel'],
        ['Capacity Rating', quote.request.selected_capacity],
        ['Input Voltage Range', quote.request.input_voltage],
        ['Output Voltage', quote.request.output_voltage],
        ['OLTC Requirement', quote.request.oltc_required],
        ['Efficiency / Losses', 'Better than 99% (Low losses 0.5-1.5%)'],
        ['Duty Cycle & Cooling', '100% Continuous Duty | Air / Oil Cooled'],
        ['Winding & Regulators', 'Heavy Section Electrolytic Rectangular Copper Strip & Carbon Roller Assembly'],
        ['Warranty', quote.warranty_terms]
    ]
    t_tech = Table(tech_data, colWidths=[180, 360])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0B192C')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    elements.append(t_tech)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph('COMMERCIAL SUMMARY', h2_style))
    comm_data = [
        ['Item Description', 'Amount (INR)'],
        [f'Ex-Factory Base Price for {quote.request.selected_capacity} Equipment', f'{quote.base_price:,.2f}'],
        [f'Goods & Services Tax (GST @ {quote.tax_percent}%)', f'{quote.tax_amount:,.2f}'],
        ['Freight & Transit Insurance', f'{quote.freight_charges:,.2f}'],
        ['Installation & Supervision Charges', f'{quote.installation_charges:,.2f}'],
        ['Total Net Amount (INR)', f'{quote.total_amount:,.2f}']
    ]
    t_comm = Table(comm_data, colWidths=[360, 180])
    t_comm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0B192C')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    elements.append(t_comm)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph('TERMS & CONDITIONS', h2_style))
    terms_text = f'''<b>Delivery Timeline:</b> {quote.delivery_timeline}<br/>
<b>Payment Terms:</b> {quote.payment_terms}<br/>
<b>Warranty:</b> {quote.warranty_terms}<br/>
<b>Testing:</b> Subject to routine, HV, and insulation tests at our testing facility in accordance with applicable electrical codes.<br/>
<b>Authorized Signatory:</b> {quote.prepared_by}'''
    elements.append(Paragraph(terms_text, body_style))

    doc.build(elements)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'{quote.quotation_number}.pdf',
        mimetype='application/pdf'
    )

@portal_bp.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('portal/orders.html', orders=orders)

@portal_bp.route('/my-invoices')
@login_required
def my_invoices():
    invoices = Invoice.query.filter_by(user_id=current_user.id).order_by(Invoice.created_at.desc()).all()
    return render_template('portal/invoices.html', invoices=invoices)

@portal_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name).strip()
        current_user.phone = request.form.get('phone', current_user.phone).strip()

        company_name = request.form.get('company_name', '').strip()
        address_line = request.form.get('address_line', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        postal_code = request.form.get('postal_code', '').strip()
        gst_number = request.form.get('gst_number', '').strip()

        if current_user.is_dealer:
            profile = current_user.dealer_profile
            if not profile:
                profile = DealerProfile(user_id=current_user.id)
                db.session.add(profile)
            profile.company_name = company_name
            profile.address_line = address_line
            profile.city = city
            profile.state = state
            profile.postal_code = postal_code
            profile.gst_number = gst_number
        else:
            profile = current_user.customer_profile
            if not profile:
                profile = CustomerProfile(user_id=current_user.id)
                db.session.add(profile)
            profile.company_name = company_name
            profile.address_line = address_line
            profile.city = city
            profile.state = state
            profile.postal_code = postal_code
            profile.gst_number = gst_number

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('portal.profile'))

    return render_template('portal/profile.html')

@portal_bp.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('portal/notifications.html', notifications=notifs)
