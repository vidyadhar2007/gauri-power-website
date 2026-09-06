from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from models import db, Product, QuotationRequest, Quotation, Order, Invoice, User, CustomerProfile
from routes_quotation import generate_rfq_number

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    products = query.all()
    return jsonify({
        'status': 'success',
        'count': len(products),
        'products': [{
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'category': p.category,
            'short_description': p.short_description,
            'capacity_range': p.capacity_range,
            'voltage_range': p.voltage_range,
            'efficiency': p.efficiency,
            'warranty': p.warranty,
            'image_url': p.image_url
        } for p in products]
    })

@api_bp.route('/products/<slug>', methods=['GET'])
def get_product(slug):
    product = Product.query.filter_by(slug=slug).first()
    if not product:
        return jsonify({'status': 'error', 'message': 'Product not found'}), 404
    return jsonify({
        'status': 'success',
        'product': {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'category': product.category,
            'short_description': product.short_description,
            'full_description': product.full_description,
            'capacity_range': product.capacity_range,
            'voltage_range': product.voltage_range,
            'efficiency': product.efficiency,
            'warranty': product.warranty,
            'salient_features': product.salient_features,
            'technical_specs': product.technical_specs,
            'applications': product.applications,
            'image_url': product.image_url
        }
    })

@api_bp.route('/config/capacities', methods=['GET'])
def get_capacities():
    capacities = [
        '25 kVA', '63 kVA', '100 kVA', '160 kVA', '200 kVA', '250 kVA',
        '300 kVA', '400 kVA', '500 kVA', '550 kVA', '630 kVA', '750 kVA',
        '800 kVA', '1000 kVA', '1250 kVA', '1500 kVA', '2000 kVA', '2500 kVA',
        '3500 kVA', '5000 kVA', '6000 kVA', 'Custom / Special Rating'
    ]
    return jsonify({
        'status': 'success',
        'capacities': capacities
    })

@api_bp.route('/quotation-requests', methods=['GET', 'POST'])
def submit_rfq():
    if request.method == 'GET':
        query = QuotationRequest.query
        if current_user.is_authenticated and not current_user.is_staff:
            query = query.filter_by(user_id=current_user.id)
        rfqs = query.order_by(QuotationRequest.created_at.desc()).limit(20).all()
        return jsonify({
            'status': 'success',
            'count': len(rfqs),
            'requests': [{
                'request_number': r.request_number,
                'customer_name': r.customer_name,
                'company_name': r.company_name,
                'capacity': r.selected_capacity,
                'status': r.status
            } for r in rfqs]
        })

    data = request.get_json() or {}
    customer_name = data.get('customer_name', '').strip()
    company_name = data.get('company_name', '').strip()
    contact_number = data.get('contact_number', '').strip()
    email = data.get('email', '').strip().lower()
    input_voltage = data.get('input_voltage', '').strip()
    output_voltage = data.get('output_voltage', '').strip()
    selected_capacity = data.get('selected_capacity', '').strip()

    if not customer_name or not company_name or not contact_number or not email or not input_voltage or not output_voltage or not selected_capacity:
        return jsonify({'status': 'error', 'message': 'Missing required fields for RFQ submission.'}), 400

    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=customer_name, email=email, phone=contact_number, role='end_customer')
            user.set_password(contact_number)
            db.session.add(user)
            db.session.flush()
        user_id = user.id

    rfq_number = generate_rfq_number()
    rfq = QuotationRequest(
        request_number=rfq_number,
        user_id=user_id,
        customer_name=customer_name,
        company_name=company_name,
        contact_number=contact_number,
        email=email,
        address_line=data.get('address_line', 'N/A'),
        city=data.get('city', 'N/A'),
        state=data.get('state', 'N/A'),
        postal_code=data.get('postal_code', 'N/A'),
        country=data.get('country', 'India'),
        product_category=data.get('product_category', 'Industrial Servo Stabilizer / VCB Switchgear'),
        input_voltage=input_voltage,
        output_voltage=output_voltage,
        selected_capacity=selected_capacity,
        suggested_transformer=data.get('suggested_transformer', 'Automatic Voltage Controller / VCB Panel'),
        oltc_required=data.get('oltc_required', 'Not Sure'),
        additional_requirements=data.get('additional_requirements', ''),
        status='Pending Sales Review'
    )
    db.session.add(rfq)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Quotation request submitted to Sales Department for review.',
        'request_number': rfq_number,
        'rfq_status': 'Pending Sales Review'
    }), 201

@api_bp.route('/quotation-requests/<request_number>', methods=['GET'])
def get_rfq_status(request_number):
    rfq = QuotationRequest.query.filter_by(request_number=request_number).first()
    if not rfq:
        return jsonify({'status': 'error', 'message': 'RFQ not found'}), 404

    return jsonify({
        'status': 'success',
        'rfq': {
            'request_number': rfq.request_number,
            'customer_name': rfq.customer_name,
            'company_name': rfq.company_name,
            'selected_capacity': rfq.selected_capacity,
            'status': rfq.status,
            'created_at': rfq.created_at.isoformat()
        }
    })

@api_bp.route('/chatbot', methods=['POST'])
def chatbot_reply():
    data = request.get_json() or {}
    user_msg = data.get('message', '').strip()
    
    if not user_msg:
        return jsonify({
            'status': 'success',
            'reply': 'Hello! I am the Gauri Power AI Technical Assistant. How can I help you today with servo voltage stabilizers, vacuum circuit breakers (VCB), or commercial quotations?',
            'suggestions': ['Calculate kVA Sizing', 'Gauri Power vs Conventional', 'Submit RFQ for Quotation', 'Factory Works & Contact']
        })
    
    q = user_msg.lower()
    
    # 1. Sizing / Capacity calculation
    if any(w in q for w in ['size', 'sizing', 'calculate', 'kva', 'capacity', 'load', 'ampere', 'current', 'kw']):
        reply = (
            "<b>Servo Stabilizer &amp; VCB Sizing Guide:</b><br><br>"
            "• <b>3-Phase (415V) Formula:</b><br>"
            "<code>kVA = (1.732 × Voltage × Full Load Amps) / 1000</code><br><br>"
            "• <b>Motor & Inductive Loads:</b><br>"
            "For continuous plant operations with induction motors, we recommend adding a <b>20% – 30% safety margin</b> to accommodate inrush starting currents.<br><br>"
            "• <b>Gauri Power Standard Capacities:</b><br>"
            "From <b>25 kVA up to 6000 kVA</b> (Custom ratings engineered on request)."
        )
        suggestions = ['Submit RFQ for Custom Sizing', 'Automatic Servo Stabilizer Specs', 'Gauri Power vs Conventional']
        
    # 2. Gauri Power vs Conventional / Toroidal / Competitors
    elif any(w in q for w in ['conventional', 'difference', 'compare', 'comparison', 'better', 'roller', 'strip', 'dimmer', 'toroidal']):
        reply = (
            "<b>The Gauri Power Engineering Difference:</b><br><br>"
            "1. <b>Regulators:</b> Wound with minimum <b>24 mm² rectangular copper strip</b> (vs conventional dimmers using max 100 mm² round wire).<br>"
            "2. <b>Contacts:</b> <b>Graphite carbon roller assemblies</b> with 8–10 years maintenance-free lifespan (no wear & tear on copper tracks).<br>"
            "3. <b>Efficiency:</b> <b>> 99% overall efficiency</b> with ultra-low losses (0.5% – 1.5%).<br>"
            "4. <b>Durability:</b> <b>20–30 years operating lifespan</b> at 100% continuous duty cycle.<br>"
            "5. <b>Warranty:</b> Full <b>5 Years Comprehensive India Warranty</b>."
        )
        suggestions = ['View Product Catalogue', 'Submit RFQ for Quotation', 'Call Technical Sales']
        
    # 3. Servo Voltage Stabilizers
    elif any(w in q for w in ['servo', 'stabilizer', 'voltage controller', 'ht servo', 'fluctuation']):
        reply = (
            "<b>Gauri Power Automatic Servo Voltage Stabilizers:</b><br><br>"
            "• <b>Capacity:</b> Up to <b>6000 kVA</b> (Balanced & Unbalanced supply types)<br>"
            "• <b>Cooling:</b> Natural Air Cooled or Mineral Oil Immersed (ONAN)<br>"
            "• <b>HT Servo Stabilizers:</b> Engineered for <b>11 kV & 33 kV</b> high-tension grids up to 10,000 kVA<br>"
            "• <b>Speed of Correction:</b> High-speed motor drive with zero waveform distortion<br>"
            "• <b>Protection:</b> Under-voltage, over-voltage, phase reversal, and electronic overload trip."
        )
        suggestions = ['Submit RFQ for Stabilizer', 'Compare with Conventional Make', 'Download Product Specs']
        
    # 4. Vacuum Circuit Breakers (VCB) & High Voltage Switchgear
    elif any(w in q for w in ['vcb', 'circuit breaker', 'switchgear', 'breaker', 'panel', 'kiosk', 'recloser', 'substation', 'interrupter']):
        reply = (
            "<b>Gauri Power High-Voltage Vacuum Circuit Breakers (Authorized Dealers & Supply):</b><br><br>"
            "In addition to manufacturing servo stabilizers, we deal in complete VCB switchgear systems:<br>"
            "• <b>Indoor Draw-Out VCB Panels:</b> 11 kV & 33 kV, 630A to 2000A, breaking capacity up to 26.3 kA / 31.5 kA.<br>"
            "• <b>Outdoor Weatherproof Kiosk VCBs:</b> IP55 enclosure with roof bushings for outdoor substations.<br>"
            "• <b>Substation Vacuum Breakers:</b> High mechanical endurance (Class M2), motorized spring charging, numerical relays.<br>"
            "• <b>Auto-Recloser Panels:</b> Pole-mounted outdoor autoreclosers for distribution feeder protection."
        )
        suggestions = ['Submit RFQ for VCB', 'VCB Panel Specifications', 'Request Single-Line Diagram']
        
    # 5. Price / Quotation / RFQ
    elif any(w in q for w in ['price', 'quotation', 'cost', 'rfq', 'rate', 'quote', 'buy', 'order']):
        reply = (
            "<b>Official Commercial Quotations:</b><br><br>"
            "As Gauri Power servo voltage stabilizers and VCB switchgear systems are heavy-duty industrial units custom-engineered to your plant's exact voltage window and load profile, <b>formal quotations are prepared individually by our Sales Engineering Department</b>.<br><br>"
            "• <b>How to get an official quote:</b><br>"
            "1. Click <b><a href='/quotation/new' class='text-power-amber underline font-bold'>Submit RFQ</a></b>.<br>"
            "2. Fill in your voltage ratings, capacity, and attach any single-line diagrams.<br>"
            "3. Our sales desk reviews the requirements and issues a detailed Commercial Quotation with PDF download."
        )
        suggestions = ['Submit RFQ Online', 'Speak With Sales Engineer', 'Check RFQ Status']
        
    # 6. Quality, Testing & Certifications
    elif any(w in q for w in ['test', 'testing', 'quality', 'is 1180', 'bee', 'iso', 'standard', 'certif']):
        reply = (
            "<b>Quality Control & Factory Testing:</b><br><br>"
            "• <b>Routine Testing (100% Units):</b> Dielectric High Voltage Breakdown, Insulation Resistance, Voltage Ratio, Vector Group, and Loss measurement.<br>"
            "• <b>Standards Compliance:</b> Adheres strictly to <b>IS 9815</b> (Servo Regulators), <b>IEC 62271-100 / IS 13118</b> (VCB Switchgear), and <b>ISO 9001:2015</b> guidelines.<br>"
            "• <b>Core & Windings:</b> Prime Cold Rolled Grain Oriented (CRGO) silicon steel & electrolytic copper strips."
        )
        suggestions = ['7-Stage Manufacturing Process', 'Submit RFQ for Quotation', 'Factory Works Info']
        
    # 7. Contact / Factory Locations
    elif any(w in q for w in ['contact', 'location', 'factory', 'plant', 'address', 'works', 'phone', 'email', 'call', 'office']):
        reply = (
            "<b>Gauri Power Facilities & Technical Contacts:</b><br><br>"
            "• <b>Registered Office & Works:</b> Vill. Nanakpura, Opp J.J. Valley, Ropar - 140001, Punjab, India<br>"
            "• <b>Direct Telephones:</b> MD: <b>+91-81789-80216</b> | Technical Head: <b>+91-78149-43673</b><br>"
            "• <b>Sales Email:</b> <b>Gauripower09@gmail.com</b>"
        )
        suggestions = ['Call MD (+91-81789-80216)', 'Call Technical Head (+91-78149-43673)', 'Submit RFQ for Quotation']
        
    # 8. Default intelligent engineering fallback
    else:
        reply = (
            f"Thank you for contacting <b>Gauri Power</b>.<br><br>"
            f"We are direct manufacturers of heavy-duty Automatic Servo Voltage Stabilizers (up to 6000 kVA) and authorized dealers in High-Voltage Vacuum Circuit Breakers (VCB 11kV & 33kV).<br><br>"
            f"Would you like technical specifications, sizing recommendations, or would you like to request an official commercial quotation?"
        )
        suggestions = ['Calculate kVA Sizing', 'Gauri Power vs Conventional', 'Submit RFQ for Quotation', 'Contact Sales Desk']
        
    return jsonify({
        'status': 'success',
        'reply': reply,
        'suggestions': suggestions
    })

