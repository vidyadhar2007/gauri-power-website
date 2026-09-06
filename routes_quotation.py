import os
from datetime import datetime, timezone
from urllib.parse import quote_plus
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_user, login_required
from models import db, QuotationRequest, User, CustomerProfile, DealerProfile, Notification, Product

quotation_bp = Blueprint('quotation', __name__)

def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'dwg'})

def generate_rfq_number():
    date_str = datetime.now().strftime('%Y%m%d')
    prefix = f'GPT-RFQ-{date_str}-'
    latest = QuotationRequest.query.filter(QuotationRequest.request_number.like(f'{prefix}%')).order_by(QuotationRequest.id.desc()).first()
    if latest:
        try:
            seq = int(latest.request_number.split('-')[-1]) + 1
        except Exception:
            seq = 1
    else:
        seq = 1
    return f'{prefix}{seq:03d}'

@quotation_bp.route('/quotation/new', methods=['GET', 'POST'], endpoint='new_rfq')
@quotation_bp.route('/quotation/submit', methods=['POST'], endpoint='submit_rfq')
def new_rfq():
    # Enforce login on GET: if user is not authenticated, redirect to login with next parameter
    if not current_user.is_authenticated:
        if request.method == 'GET':
            flash('Please sign in or create an account to request an official quotation. Let us know whether you are an End Customer or Authorized Dealer.', 'info')
            return redirect(url_for('auth.login', next=request.url))

    preselected_slug = request.args.get('product')
    preselected_product = None
    if preselected_slug:
        preselected_product = Product.query.filter_by(slug=preselected_slug).first()
    if not preselected_product and request.form.get('product_id'):
        preselected_product = Product.query.get(request.form.get('product_id'))

    products = Product.query.all()

    if request.method == 'POST':
        # Customer / Organization identity
        customer_type = (request.form.get('customer_type') or request.form.get('role') or 'End Customer').strip()
        customer_name = (request.form.get('customer_name') or request.form.get('contact_name', '')).strip()
        company_name = request.form.get('company_name', '').strip()
        contact_number = (request.form.get('contact_number') or request.form.get('phone', '')).strip()
        email = request.form.get('email', '').strip().lower()
        address_line = (request.form.get('address_line') or request.form.get('site_location', '')).strip()
        city = request.form.get('city', 'Industrial Zone').strip()
        state = request.form.get('state', 'Punjab').strip()
        postal_code = request.form.get('postal_code', '140001').strip()
        country = request.form.get('country', 'India').strip()
        gstin = request.form.get('gstin', '').strip()

        # Technical Requirements
        product_category = request.form.get('product_category', '').strip()
        input_voltage = request.form.get('input_voltage', '').strip()
        output_voltage = request.form.get('output_voltage', '').strip()
        selected_capacity = (request.form.get('selected_capacity') or request.form.get('capacity_kva', '')).strip()
        suggested_transformer = request.form.get('suggested_transformer', '').strip()
        phase = request.form.get('phase', '3-Phase 4-Wire').strip()
        winding_material = request.form.get('winding_material', 'Electrolytic Copper Strip (>=24 mm²)').strip()
        cooling_type = request.form.get('cooling_type', 'Oil Cooled (ONAN with Radiators)').strip()
        quantity = request.form.get('quantity', '1').strip()
        oltc_required = request.form.get('oltc_required', 'Not Sure').strip()
        additional_notes = (request.form.get('additional_requirements') or request.form.get('additional_notes', '')).strip()

        if not customer_name or not company_name or not contact_number or not email or not address_line:
            flash('Please complete all mandatory customer and company details.', 'error')
            return render_template('quotation/rfq_stepper.html', form_data=request.form, preselected_product=preselected_product, products=products)

        if not input_voltage or not output_voltage or not selected_capacity:
            flash('Please specify input voltage, output voltage, and equipment capacity.', 'error')
            return render_template('quotation/rfq_stepper.html', form_data=request.form, preselected_product=preselected_product, products=products)

        # Ensure user account
        if current_user.is_authenticated:
            user = current_user
        else:
            user = User.query.filter_by(email=email).first()
            if not user:
                user_role = 'dealer' if 'dealer' in customer_type.lower() else 'end_customer'
                user = User(
                    name=customer_name,
                    email=email,
                    phone=contact_number,
                    role=user_role
                )
                user.set_password(contact_number)
                db.session.add(user)
                db.session.flush()

                if user_role == 'dealer':
                    d_profile = DealerProfile(
                        user_id=user.id,
                        company_name=company_name,
                        gst_number=gstin,
                        address_line=address_line,
                        city=city,
                        state=state,
                        postal_code=postal_code,
                        country=country
                    )
                    db.session.add(d_profile)
                else:
                    cust_profile = CustomerProfile(
                        user_id=user.id,
                        company_name=company_name,
                        gst_number=gstin,
                        address_line=address_line,
                        city=city,
                        state=state,
                        postal_code=postal_code,
                        country=country
                    )
                    db.session.add(cust_profile)
                db.session.flush()
            login_user(user)

        # File upload handling
        uploaded_doc_name = None
        uploaded_doc_path = None
        file = request.files.get('specification_file') or request.files.get('spec_sheet')
        if file and file.filename and allowed_file(file.filename):
            fname = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            saved_filename = f'{timestamp}_{fname}'
            save_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(save_dir, exist_ok=True)
            full_path = os.path.join(save_dir, saved_filename)
            file.save(full_path)
            uploaded_doc_name = fname
            uploaded_doc_path = f'uploads/{saved_filename}'

        # Format composite requirements note
        structured_notes = f"[Client Type: {customer_type}] [Phase: {phase}] [Winding: {winding_material}] [Cooling: {cooling_type}] [Qty: {quantity}]"
        if gstin:
            structured_notes += f" [GSTIN: {gstin}]"
        if additional_notes:
            structured_notes += f"\nCustomer Notes: {additional_notes}"

        rfq_number = generate_rfq_number()

        rfq = QuotationRequest(
            request_number=rfq_number,
            user_id=user.id,
            customer_name=customer_name,
            company_name=company_name,
            contact_number=contact_number,
            email=email,
            address_line=address_line,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            customer_type=customer_type,
            product_category=product_category or (preselected_product.name if preselected_product else 'Automatic Servo Voltage Stabilizer'),
            input_voltage=input_voltage,
            output_voltage=output_voltage,
            selected_capacity=selected_capacity,
            suggested_transformer=suggested_transformer or (preselected_product.name if preselected_product else 'Automatic Voltage Controller (Industrial Grade)'),
            oltc_required=oltc_required,
            additional_requirements=structured_notes,
            uploaded_document_name=uploaded_doc_name,
            uploaded_document_path=uploaded_doc_path,
            status='Pending Sales Review'
        )
        db.session.add(rfq)

        # Notify customer in portal
        notification = Notification(
            user_id=user.id,
            title=f'Quotation Request Logged: {rfq_number}',
            message=f'Your quotation request for {selected_capacity} {rfq.product_category} has been routed to Gauri Power MD (+91-81789-80216). We will prepare and deliver your official quotation in PDF form.',
            type='success',
            link_url=f'/my-requests/{rfq_number}'
        )
        db.session.add(notification)
        db.session.commit()

        # Log dispatch to official company contact number
        current_app.logger.info(
            f"QUOTATION REQUEST DISPATCHED TO GAURI POWER MD CONTACT NUMBER +918178980216: "
            f"Ref: {rfq_number} | Type: {customer_type} | Client: {customer_name} ({company_name}) | "
            f"Equip: {selected_capacity} {rfq.product_category}"
        )

        return redirect(url_for('quotation.rfq_success', request_number=rfq_number))

    # GET Request: prefill credentials from current user
    form_data = {}
    if current_user.is_authenticated:
        form_data = {
            'customer_name': current_user.name,
            'company_name': current_user.company_name or '',
            'contact_number': current_user.phone or '',
            'email': current_user.email or '',
            'customer_type': 'Authorized Dealer' if current_user.is_dealer else 'End Customer',
        }
        profile = current_user.dealer_profile if current_user.is_dealer else current_user.customer_profile
        if profile:
            form_data.update({
                'address_line': getattr(profile, 'address_line', ''),
                'city': getattr(profile, 'city', ''),
                'state': getattr(profile, 'state', ''),
                'postal_code': getattr(profile, 'postal_code', ''),
                'country': getattr(profile, 'country', 'India'),
                'gstin': getattr(profile, 'gst_number', '')
            })

    return render_template(
        'quotation/rfq_stepper.html',
        form_data=form_data,
        preselected_product=preselected_product,
        products=products
    )

@quotation_bp.route('/quotation/thank-you/<request_number>')
@quotation_bp.route('/quotation/success/<request_number>')
def rfq_success(request_number):
    rfq = QuotationRequest.query.filter_by(request_number=request_number).first_or_404()

    # Formulate pre-filled WhatsApp message for company contact number 8178980216
    client_type = getattr(rfq, 'customer_type', None) or ('Authorized Dealer' if (rfq.user and rfq.user.is_dealer) else 'End Customer')
    wa_msg = (
        f"Hello Gauri Power Team,\n\n"
        f"I have submitted an official quotation request on your website.\n\n"
        f"📌 *RFQ Ref:* {rfq.request_number}\n"
        f"👤 *Client Type:* {client_type}\n"
        f"🏢 *Company:* {rfq.company_name}\n"
        f"🧑 *Contact Person:* {rfq.customer_name}\n"
        f"📞 *Phone:* {rfq.contact_number}\n"
        f"✉️ *Email:* {rfq.email}\n"
        f"📍 *Site Location:* {rfq.address_line}, {rfq.city}, {rfq.state}\n"
        f"⚡ *Equipment:* {rfq.product_category}\n"
        f"📊 *Capacity:* {rfq.selected_capacity}\n"
        f"🔌 *Voltage:* In: {rfq.input_voltage} | Out: {rfq.output_voltage}\n\n"
        f"Please review our technical requirements and share the official quotation in PDF format. Thank you!"
    )
    whatsapp_url = f"https://wa.me/918178980216?text={quote_plus(wa_msg)}"

    return render_template(
        'quotation/success.html',
        rfq=rfq,
        whatsapp_url=whatsapp_url,
        company_phone='8178980216'
    )
