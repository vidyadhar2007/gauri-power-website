import os
import io
from app import create_app
from models import db, User, Product, QuotationRequest, Quotation, Order, Invoice

app = create_app()

def run_tests():
    print("=" * 70)
    print("STARTING GAURI POWER SYSTEM VERIFICATION TEST SUITE")
    print("=" * 70)

    with app.test_client() as client:
        # Test 1: Public Pages
        print("\n--- TEST 1: Public Corporate Pages ---")
        public_urls = [
            '/',
            '/about',
            '/products',
            '/manufacturing',
            '/quality',
            '/projects',
            '/certifications',
            '/contact',
            '/privacy-policy',
            '/terms',
            '/ai-assistant'
        ]
        for url in public_urls:
            res = client.get(url)
            assert res.status_code == 200, f"Failed GET {url} with status {res.status_code}"
            print(f"  [PASS] GET {url:<25} -> 200 OK")

        # Test 2: Product Detail Pages for all seeded products
        print("\n--- TEST 2: Product Detail Pages ---")
        product_slugs = []
        with app.app_context():
            products = Product.query.all()
            assert len(products) >= 8, f"Expected at least 8 products, found {len(products)}"
            product_slugs = [(p.slug, p.name) for p in products]

        import html
        for slug, name in product_slugs:
            res = client.get(f'/products/{slug}')
            assert res.status_code == 200, f"Failed GET /products/{slug}"
            assert html.escape(name).encode('utf-8') in res.data, f"Product name missing in /products/{slug}"
            print(f"  [PASS] GET /products/{slug:<35} -> 200 OK (Verified '{name[:25]}...')")

        # Test 3: Authentication & Role Restrictions
        print("\n--- TEST 3: Authentication & Role Restrictions ---")
        
        # 3.1 Unauthenticated portal access redirected to login
        res = client.get('/dashboard', follow_redirects=False)
        assert res.status_code == 302 and '/login' in res.headers['Location'], "Unauthenticated portal access not redirected"
        print("  [PASS] Unauthenticated GET /dashboard -> 302 Redirect to /login")

        # 3.2 Unauthenticated staff access redirected
        res = client.get('/internal/dashboard', follow_redirects=False)
        assert res.status_code == 302, "Unauthenticated staff access not redirected"
        print("  [PASS] Unauthenticated GET /internal/dashboard -> 302 Redirect")

        # 3.3 Customer Login
        res = client.post('/login', data={
            'email': 'customer@industrial.com',
            'password': 'Customer@123'
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b"Welcome back, Rajesh Sharma" in res.data or b"Dashboard" in res.data
        print("  [PASS] End Customer Login (customer@industrial.com) -> Authenticated Successfully")

        # Customer tries to access staff desk -> Should be 403 Forbidden
        res = client.get('/internal/dashboard')
        assert res.status_code == 403, f"Expected 403 for Customer accessing /internal/dashboard, got {res.status_code}"
        print("  [PASS] Customer accessing /internal/dashboard -> 403 Access Forbidden (Security Passed)")

        # Customer logout
        client.get('/logout', follow_redirects=True)

        # 3.4 Staff Login
        res = client.post('/internal/login', data={
            'email': 'sales@gauripower.in',
            'password': 'Sales@123'
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b"Sales & Engineering Review Portal" in res.data or b"Sales Desk" in res.data
        print("  [PASS] Sales Staff Login (sales@gauripower.in) -> Authenticated Successfully")
        client.get('/logout', follow_redirects=True)

        # Test 4: STRICT RFQ RULE & COMPLETE B2B WORKFLOW
        print("\n--- TEST 4: STRICT RFQ RULE & COMPLETE B2B WORKFLOW ---")
        print("  Checking Directive: RFQ creates NO price, NO quotation, NO order, NO invoice.")

        # Log in as Customer
        client.post('/login', data={'email': 'customer@industrial.com', 'password': 'Customer@123'})

        with app.app_context():
            prod = Product.query.first()
            prod_id = prod.id
            prod_slug = prod.slug

        # Submit new RFQ with mock drawing file
        rfq_payload = {
            'contact_name': 'Vikram Mehra',
            'email': 'vikram@punjabfoundry.com',
            'phone': '+91 98765 11223',
            'company_name': 'Mehra Induction Furnaces Ltd',
            'site_location': 'Mandi Gobindgarh',
            'state': 'Punjab',
            'gstin': '03AABCM9988Z1Z2',
            'product_id': prod_id,
            'capacity_kva': '3000 kVA',
            'input_voltage': '320V - 470V AC',
            'output_voltage': '415V ± 1% AC',
            'phase': '3-Phase 4-Wire',
            'winding_material': 'Electrolytic Copper Strip (>=24 mm²)',
            'cooling_type': 'Oil Cooled (ONAN with Radiators)',
            'quantity': 1,
            'additional_notes': 'Must withstand heavy furnace surge loads with graphite carbon rollers.',
            'spec_sheet': (io.BytesIO(b"%PDF-1.4 Mock SLD Single Line Diagram content"), 'foundry_sld.pdf')
        }

        res = client.post('/quotation/submit', data=rfq_payload, content_type='multipart/form-data', follow_redirects=True)
        assert res.status_code == 200
        assert b"Pending Sales Review" in res.data or b"GPT-RFQ-" in res.data
        print("  [PASS] RFQ Submission succeeded with drawing upload")

        with app.app_context():
            new_rfq = QuotationRequest.query.filter_by(company_name='Mehra Induction Furnaces Ltd').order_by(QuotationRequest.id.desc()).first()
            assert new_rfq is not None, "New RFQ was not found in database"
            
            # STRICT QUOTATION RULE VERIFICATIONS:
            print("  --- STRICT QUOTATION RULE VERIFICATION ---")
            assert new_rfq.status == 'Pending Sales Review', f"Expected status 'Pending Sales Review', got '{new_rfq.status}'"
            print("    [PASS] RFQ Status is initialized strictly to 'Pending Sales Review'")

            # Check that QuotationRequest does NOT have price attribute / no quotation created
            assert not hasattr(new_rfq, 'price') or getattr(new_rfq, 'price', None) is None, "RFQ contains calculated price!"
            print("    [PASS] RFQ does NOT contain or generate price (Strict compliance with User Directive)")

            # Check that NO quotation exists yet for this RFQ
            quotes_for_rfq = Quotation.query.filter_by(request_id=new_rfq.id).all()
            assert len(quotes_for_rfq) == 0, f"Expected 0 quotations, found {len(quotes_for_rfq)}!"
            print("    [PASS] Zero quotations automatically generated for this RFQ (Manual Sales Issuance Rule Preserved)")

            # Check that NO order exists yet
            orders_for_rfq = Order.query.join(Quotation).filter(Quotation.request_id == new_rfq.id).all()
            assert len(orders_for_rfq) == 0, f"Expected 0 orders, found {len(orders_for_rfq)}!"
            print("    [PASS] Zero orders automatically generated for this RFQ (Order Confirmation Rule Preserved)")

            rfq_num = new_rfq.request_number

        # Log out customer, log in as Sales Staff
        client.get('/logout')
        client.post('/internal/login', data={'email': 'sales@gauripower.in', 'password': 'Sales@123'})

        # Staff reviews RFQ
        res = client.get(f'/internal/rfq/{rfq_num}')
        assert res.status_code == 200
        print(f"  [PASS] Sales Staff successfully retrieved RFQ details at /internal/rfq/{rfq_num}")

        # Staff updates status to Under Technical Review
        res = client.post(f'/internal/rfq/{rfq_num}/status', data={'status': 'Under Technical Review'}, follow_redirects=True)
        assert res.status_code == 200

        # Staff prepares and officially issues Quotation
        quote_payload = {
            'base_price': 1450000.00,
            'freight_charges': 35000.00,
            'tax_rate': 18.0,
            'delivery_timeline_weeks': 4,
            'warranty_terms': '5 Years Warranty in India with Graphite Rollers',
            'payment_terms': '30% advance with PO, 70% against Proforma Invoice prior to dispatch',
            'notes': 'Fabrication adhering strictly to IS 9815 and IS 2026 standards.'
        }
        res = client.post(f'/internal/rfq/{rfq_num}/quote', data=quote_payload, follow_redirects=True)
        assert res.status_code == 200

        with app.app_context():
            issued_quote = Quotation.query.join(QuotationRequest).filter(QuotationRequest.request_number == rfq_num).first()
            assert issued_quote is not None, "Quotation was not created by Sales Staff"
            assert issued_quote.status == 'Issued', f"Expected quote status 'Issued', got {issued_quote.status}"
            assert issued_quote.base_price == 1450000.00
            assert issued_quote.tax_amount == (1450000.00 + 35000.00) * 0.18
            assert issued_quote.total_amount == (1450000.00 + 35000.00) * 1.18
            quote_num = issued_quote.quotation_number
            print(f"  [PASS] Sales Staff officially issued Quotation {quote_num} for INR {issued_quote.total_amount:,.2f}")

        # Customer logs back in, reviews Quotation, and Accepts it
        client.get('/logout')
        client.post('/login', data={'email': 'customer@industrial.com', 'password': 'Customer@123'})

        res = client.get(f'/my-quotations/{quote_num}')
        assert res.status_code == 200
        print(f"  [PASS] Customer reviewed official Quotation {quote_num}")

        # Test PDF Generation
        res = client.get(f'/my-quotations/{quote_num}/pdf')
        assert res.status_code == 200
        assert res.headers['Content-Type'] == 'application/pdf'
        assert res.data.startswith(b'%PDF'), "PDF content is not valid PDF binary"
        print(f"  [PASS] ReportLab Quotation PDF generated successfully ({len(res.data)} bytes, %PDF-1.4 header)")

        # Customer Accepts Quotation
        res = client.post(f'/my-quotations/{quote_num}/accept', data={'po_number': 'PO/MEHRA/2026/099'}, follow_redirects=True)
        assert res.status_code == 200

        with app.app_context():
            accepted_quote = Quotation.query.filter_by(quotation_number=quote_num).first()
            assert accepted_quote.status == 'Accepted', f"Expected quote status 'Accepted', got {accepted_quote.status}"
            
            confirmed_order = Order.query.filter_by(quotation_id=accepted_quote.id).first()
            assert confirmed_order is not None, "Order was not created upon quotation acceptance"
            assert confirmed_order.status == 'Order Confirmed'
            assert confirmed_order.production_stage == 'Order Confirmed'
            order_num = confirmed_order.order_number
            print(f"  [PASS] Customer accepted Quotation -> Confirmed Order created: {order_num}")

        # Staff advances order through the 7-stage production milestones to Dispatched
        client.get('/logout')
        client.post('/internal/login', data={'email': 'sales@gauripower.in', 'password': 'Sales@123'})

        stages_to_advance = [
            'Engineering & Drawing Approval',
            'Raw Material Inward & Core Stacking',
            'Electrolytic Copper Coil Winding',
            'Core-Coil Assembly & Tanking',
            'Routine & Dielectric HV Testing',
            'Final Quality Inspection & Dispatched'
        ]
        for stg in stages_to_advance:
            res = client.post(f'/internal/order/{order_num}/stage', data={'production_stage': stg}, follow_redirects=True)
            assert res.status_code == 200
            print(f"    -> Advanced production milestone to: '{stg}'")

        with app.app_context():
            final_order = Order.query.filter_by(order_number=order_num).first()
            assert 'Dispatched' in final_order.status
            # Check that Invoice was automatically generated upon reaching Dispatched
            invoice = Invoice.query.filter_by(order_id=final_order.id).first()
            assert invoice is not None, "Invoice was not generated on dispatch"
            assert invoice.total_amount == final_order.total_amount
            print(f"  [PASS] Reached Dispatched Stage -> Commercial Tax Invoice generated: {invoice.invoice_number} (INR {invoice.total_amount:,.2f})")

        # Test 5: REST API Verification
        print("\n--- TEST 5: REST API Layer Verification ---")
        res = client.get('/api/v1/products')
        assert res.status_code == 200
        json_data = res.get_json()
        assert json_data['status'] == 'success'
        assert len(json_data['products']) >= 8
        print(f"  [PASS] GET /api/v1/products -> 200 OK ({len(json_data['products'])} products returned)")

        res = client.get(f"/api/v1/products/{prod_slug}")
        assert res.status_code == 200
        json_data = res.get_json()
        assert json_data['status'] == 'success'
        assert json_data['product']['slug'] == prod_slug
        print(f"  [PASS] GET /api/v1/products/{prod_slug} -> 200 OK")

        res = client.get('/api/v1/config/capacities')
        assert res.status_code == 200
        json_data = res.get_json()
        assert 'capacities' in json_data
        print(f"  [PASS] GET /api/v1/config/capacities -> 200 OK ({len(json_data['capacities'])} standard ratings)")

        res = client.get('/api/v1/quotation-requests')
        assert res.status_code == 200
        json_data = res.get_json()
        assert json_data['count'] >= 1
        print(f"  [PASS] GET /api/v1/quotation-requests -> 200 OK ({json_data['count']} RFQs registered)")

    print("\n" + "=" * 70)
    print("ALL 5 TEST PHASES PASSED WITH 100% SUCCESS!")
    print("GAURI POWER SYSTEM FULLY VERIFIED AND OPERATIONAL.")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()

