import os
from datetime import datetime, timezone, timedelta, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, QuotationRequest, Quotation, Order, Invoice, Notification, User
from auth import staff_required

internal_bp = Blueprint('internal', __name__, url_prefix='/internal')

def generate_quotation_number():
    date_str = datetime.now().strftime('%Y%m%d')
    prefix = f'GPT-QT-{date_str}-'
    latest = Quotation.query.filter(Quotation.quotation_number.like(f'{prefix}%')).order_by(Quotation.id.desc()).first()
    seq = (int(latest.quotation_number.split('-')[-1]) + 1) if latest else 1
    return f'{prefix}{seq:03d}'

@internal_bp.route('/dashboard')
@staff_required
def dashboard():
    total_rfqs = QuotationRequest.query.count()
    pending_rfqs = QuotationRequest.query.filter_by(status='Pending Sales Review').count()
    under_review_rfqs = QuotationRequest.query.filter_by(status='Under Technical Review').count()
    quotes_prepared = Quotation.query.count()
    active_orders = Order.query.filter(Order.status != 'Delivered').count()

    recent_rfqs = QuotationRequest.query.order_by(QuotationRequest.created_at.desc()).limit(8).all()
    recent_quotes = Quotation.query.order_by(Quotation.created_at.desc()).limit(5).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    stats = {
        'total_rfqs': total_rfqs,
        'pending_rfqs': pending_rfqs,
        'under_review_rfqs': under_review_rfqs,
        'quotes_prepared': quotes_prepared,
        'active_orders': active_orders
    }

    return render_template(
        'internal/dashboard.html',
        stats=stats,
        pending_rfqs_count=pending_rfqs,
        total_rfqs_count=total_rfqs,
        total_quotations_count=quotes_prepared,
        active_orders_count=active_orders,
        recent_rfqs=recent_rfqs,
        recent_quotes=recent_quotes,
        recent_orders=recent_orders
    )

@internal_bp.route('/rfqs')
@staff_required
def rfq_list():
    status_filter = request.args.get('status', 'all')
    query = QuotationRequest.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    rfqs = query.order_by(QuotationRequest.created_at.desc()).all()
    return render_template('internal/rfq_list.html', rfqs=rfqs, current_filter=status_filter)

@internal_bp.route('/rfq/<request_number>')
@staff_required
def rfq_detail(request_number):
    rfq = QuotationRequest.query.filter_by(request_number=request_number).first_or_404()
    quotation = Quotation.query.filter_by(request_id=rfq.id).first()
    return render_template('internal/rfq_detail.html', rfq=rfq, quotation=quotation)

@internal_bp.route('/rfq/<request_number>/update-status', methods=['POST'])
@internal_bp.route('/rfq/<request_number>/status', methods=['POST'])
@staff_required
def update_rfq_status(request_number):
    rfq = QuotationRequest.query.filter_by(request_number=request_number).first_or_404()
    new_status = request.form.get('status')
    sales_notes = request.form.get('sales_notes', '').strip()

    valid_statuses = [
        'Pending Sales Review',
        'Under Technical Review',
        'Quotation Under Preparation',
        'Quotation Sent',
        'Quotation Issued',
        'Closed'
    ]
    if new_status in valid_statuses:
        rfq.status = new_status
        if sales_notes:
            rfq.sales_notes = sales_notes

        # Send notification to customer
        notif = Notification(
            user_id=rfq.user_id,
            title=f'RFQ Status Updated: {rfq.request_number}',
            message=f'Your equipment request status has been updated to: "{new_status}".',
            type='info',
            link_url=f'/my-requests/{rfq.request_number}'
        )
        db.session.add(notif)
        db.session.commit()
        flash(f'RFQ {request_number} updated to "{new_status}".', 'success')
    else:
        flash('Invalid status specified.', 'error')

    return redirect(url_for('internal.rfq_detail', request_number=request_number))

@internal_bp.route('/rfq/<request_number>/quote', methods=['GET', 'POST'], endpoint='create_quotation')
@internal_bp.route('/rfq/<request_number>/prepare-quote', methods=['GET', 'POST'], endpoint='prepare_quotation')
@staff_required
def create_quotation(request_number):
    rfq = QuotationRequest.query.filter_by(request_number=request_number).first_or_404()
    existing_quote = Quotation.query.filter_by(request_id=rfq.id).first()

    if request.method == 'POST':
        try:
            base_price = float(request.form.get('base_price', 0))
            tax_percent = float(request.form.get('tax_percent') or request.form.get('tax_rate', 18.0))
            freight_charges = float(request.form.get('freight_charges', 0))
            installation_charges = float(request.form.get('installation_charges', 0))
            delivery_timeline = request.form.get('delivery_timeline') or f"{request.form.get('delivery_timeline_weeks', 4)} weeks"
            payment_terms = request.form.get('payment_terms', '30% advance with PO, 70% against proforma before dispatch')
            warranty_terms = request.form.get('warranty_terms', '5 Years Manufacturer Warranty in India')
            valid_days = int(request.form.get('valid_days', 30))
            commercial_notes = (request.form.get('commercial_notes') or request.form.get('notes', '')).strip()

            subtotal = base_price + freight_charges + installation_charges
            tax_amount = round(subtotal * (tax_percent / 100.0), 2)
            total_amount = round(subtotal + tax_amount, 2)
            valid_until = date.today() + timedelta(days=valid_days)

            if existing_quote:
                quote = existing_quote
                quote.base_price = base_price
                quote.tax_percent = tax_percent
                quote.tax_amount = tax_amount
                quote.freight_charges = freight_charges
                quote.installation_charges = installation_charges
                quote.total_amount = total_amount
                quote.valid_until = valid_until
                quote.delivery_timeline = delivery_timeline
                quote.payment_terms = payment_terms
                quote.warranty_terms = warranty_terms
                quote.commercial_terms = commercial_notes
                quote.status = 'Issued'
            else:
                quote_number = generate_quotation_number()
                quote = Quotation(
                    quotation_number=quote_number,
                    request_id=rfq.id,
                    user_id=rfq.user_id,
                    prepared_by=f'{current_user.name} (Sales Engineering)',
                    base_price=base_price,
                    tax_percent=tax_percent,
                    tax_amount=tax_amount,
                    freight_charges=freight_charges,
                    installation_charges=installation_charges,
                    total_amount=total_amount,
                    valid_until=valid_until,
                    delivery_timeline=delivery_timeline,
                    payment_terms=payment_terms,
                    warranty_terms=warranty_terms,
                    commercial_terms=commercial_notes,
                    status='Issued'
                )
                db.session.add(quote)

            rfq.status = 'Quotation Issued'

            # Notify customer of official quote
            notif = Notification(
                user_id=rfq.user_id,
                title=f'Official Quotation Received: {quote.quotation_number}',
                message=f'Gauri Power Sales Department has prepared and released the official commercial quotation for your {rfq.selected_capacity} equipment requirement.',
                type='success',
                link_url=f'/my-quotations/{quote.quotation_number}'
            )
            db.session.add(notif)
            db.session.commit()

            flash(f'Official Quotation {quote.quotation_number} successfully prepared and sent to customer!', 'success')
            return redirect(url_for('internal.rfq_detail', request_number=request_number))

        except Exception as e:
            flash(f'Error creating quotation: {str(e)}', 'error')

    return render_template('internal/create_quotation.html', rfq=rfq, quote=existing_quote)

@internal_bp.route('/orders')
@staff_required
def order_list():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('internal/order_list.html', orders=orders)

@internal_bp.route('/order/<order_number>/update-status', methods=['POST'])
@internal_bp.route('/order/<order_number>/stage', methods=['POST'], endpoint='update_order_stage')
@staff_required
def update_order_status(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    new_status = request.form.get('production_stage') or request.form.get('status')
    carrier = request.form.get('carrier_details', '').strip()
    tracking = request.form.get('tracking_reference', '').strip()
    est_delivery = request.form.get('estimated_delivery', '').strip()

    valid_statuses = [
        'Order Confirmed',
        'Engineering & Drawing Approval',
        'Raw Material Inward & Core Stacking',
        'Electrolytic Copper Coil Winding',
        'Core-Coil Assembly & Tanking',
        'Routine & Dielectric HV Testing',
        'Final Quality Inspection & Dispatched',
        'Production Started',
        'Under Manufacturing',
        'Quality Testing',
        'Ready for Dispatch',
        'Dispatched',
        'Delivered'
    ]

    if new_status in valid_statuses:
        order.status = new_status
        if carrier:
            order.carrier_details = carrier
        if tracking:
            order.tracking_reference = tracking
        if est_delivery:
            order.estimated_delivery = est_delivery

        # If final dispatched or delivered, generate invoice if not exists
        if new_status in ['Final Quality Inspection & Dispatched', 'Dispatched', 'Delivered']:
            existing_inv = Invoice.query.filter_by(order_id=order.id).first()
            if not existing_inv:
                date_str = datetime.now().strftime('%Y%m%d')
                inv_num = f'GPT-INV-{date_str}-{order.id:03d}'
                inv = Invoice(
                    invoice_number=inv_num,
                    order_id=order.id,
                    user_id=order.user_id,
                    invoice_date=date.today(),
                    due_date=date.today() + timedelta(days=15),
                    taxable_amount=order.quotation.base_price,
                    tax_amount=order.quotation.tax_amount,
                    total_amount=order.total_amount,
                    status='Issued'
                )
                db.session.add(inv)

        # Send customer notification
        notif = Notification(
            user_id=order.user_id,
            title=f'Order Update: {order.order_number}',
            message=f'Your order status has advanced to: "{new_status}".',
            type='info',
            link_url='/my-orders'
        )
        db.session.add(notif)
        db.session.commit()

        flash(f'Order {order_number} status updated to "{new_status}".', 'success')
    else:
        flash('Invalid order status.', 'error')

    return redirect(url_for('internal.order_list'))
