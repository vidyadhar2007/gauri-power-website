import os
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default='end_customer') # 'dealer', 'end_customer', 'sales_staff', 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    dealer_profile = db.relationship('DealerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    customer_profile = db.relationship('CustomerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    quotation_requests = db.relationship('QuotationRequest', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    quotations = db.relationship('Quotation', backref='user', lazy='dynamic')
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    invoices = db.relationship('Invoice', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_dealer(self):
        return self.role == 'dealer'

    @property
    def is_customer(self):
        return self.role == 'end_customer'

    @property
    def is_staff(self):
        return self.role in ('sales_staff', 'admin')

    @property
    def company_name(self):
        if self.is_dealer and self.dealer_profile:
            return self.dealer_profile.company_name
        elif self.is_customer and self.customer_profile:
            return self.customer_profile.company_name
        return ''


class DealerProfile(db.Model):
    __tablename__ = 'dealer_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    gst_number = db.Column(db.String(50), nullable=True)
    dealership_code = db.Column(db.String(50), nullable=True)
    address_line = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(30), nullable=False)
    country = db.Column(db.String(100), default='India')
    territory = db.Column(db.String(150), nullable=True)


class CustomerProfile(db.Model):
    __tablename__ = 'customer_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=True)
    industry_type = db.Column(db.String(100), nullable=True)
    gst_number = db.Column(db.String(50), nullable=True)
    address_line = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(30), nullable=False)
    country = db.Column(db.String(100), default='India')


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    full_description = db.Column(db.Text, nullable=False)
    capacity_range = db.Column(db.String(100), nullable=False)
    voltage_range = db.Column(db.String(100), nullable=False)
    efficiency = db.Column(db.String(50), default='> 99%')
    warranty = db.Column(db.String(50), default='5 Years in India')
    cooling_type = db.Column(db.String(100), default='Air Cooled / Oil Cooled')
    duty_cycle = db.Column(db.String(100), default='100% Continuous')
    salient_features = db.Column(db.JSON, nullable=True)
    technical_specs = db.Column(db.JSON, nullable=True)
    applications = db.Column(db.JSON, nullable=True)
    image_url = db.Column(db.String(255), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)


class QuotationRequest(db.Model):
    __tablename__ = 'quotation_requests'

    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    customer_name = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    contact_number = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    address_line = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(30), nullable=False)
    country = db.Column(db.String(100), default='India')

    customer_type = db.Column(db.String(50), default='End Customer', nullable=True)
    product_category = db.Column(db.String(100), nullable=True)
    input_voltage = db.Column(db.String(100), nullable=False)
    output_voltage = db.Column(db.String(100), nullable=False)
    selected_capacity = db.Column(db.String(100), nullable=False)
    suggested_transformer = db.Column(db.String(255), nullable=True)
    suggestion_disclaimer = db.Column(
        db.String(255),
        default='Preliminary algorithmic recommendation. Not an official technical approval. Our technical team will review specifications.'
    )
    oltc_required = db.Column(db.String(30), nullable=False, default='Not Sure')
    additional_requirements = db.Column(db.Text, nullable=True)
    uploaded_document_name = db.Column(db.String(255), nullable=True)
    uploaded_document_path = db.Column(db.String(255), nullable=True)

    status = db.Column(db.String(50), default='Pending Sales Review', nullable=False, index=True)
    sales_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    quotations = db.relationship('Quotation', backref='request', lazy='dynamic')

    @property
    def contact_name(self):
        return self.customer_name

    @property
    def phone(self):
        return self.contact_number

    @property
    def suggested_equipment(self):
        return self.suggested_transformer

    @suggested_equipment.setter
    def suggested_equipment(self, value):
        self.suggested_transformer = value

    @property
    def capacity_kva(self):
        return self.selected_capacity

    @property
    def site_location(self):
        return self.address_line

    @property
    def file_attachment(self):
        return self.uploaded_document_name

    @property
    def additional_notes(self):
        return self.additional_requirements

    @property
    def quantity(self):
        return 1

    @property
    def phase(self):
        return '3-Phase 4-Wire'

    @property
    def winding_material(self):
        return 'Electrolytic Copper Strip (>=24 mm²)'

    @property
    def cooling_type(self):
        return 'Oil Cooled (ONAN)'

    @property
    def product(self):
        return Product.query.filter((Product.category == self.product_category) | (Product.name == self.product_category)).first()


class Quotation(db.Model):
    __tablename__ = 'quotations'

    id = db.Column(db.Integer, primary_key=True)
    quotation_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    request_id = db.Column(db.Integer, db.ForeignKey('quotation_requests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prepared_by = db.Column(db.String(150), default='Gauri Power Sales Engineering Team')
    
    base_price = db.Column(db.Float, nullable=False)
    tax_percent = db.Column(db.Float, default=18.0)
    tax_amount = db.Column(db.Float, nullable=False)
    freight_charges = db.Column(db.Float, default=0.0)
    installation_charges = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='INR')

    valid_until = db.Column(db.Date, nullable=False)
    delivery_timeline = db.Column(db.String(100), default='2 to 4 weeks from order confirmation')
    payment_terms = db.Column(db.String(255), default='30% advance with PO, 70% against proforma before dispatch')
    warranty_terms = db.Column(db.String(255), default='5 Years Manufacturer Warranty in India')
    technical_specifications = db.Column(db.Text, nullable=True)
    commercial_terms = db.Column(db.Text, nullable=True)
    pdf_document_path = db.Column(db.String(255), nullable=True)

    status = db.Column(db.String(50), default='Sent', nullable=False)
    customer_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    orders = db.relationship('Order', backref='quotation', lazy='dynamic')

    @property
    def validity_date(self):
        return self.valid_until

    @property
    def delivery_timeline_weeks(self):
        try:
            for w in (self.delivery_timeline or '').split():
                if w.isdigit():
                    return int(w)
            return 4
        except Exception:
            return 4

    @property
    def issuer(self):
        class Issuer:
            name = self.prepared_by or 'Sales Engineering Desk'
        return Issuer()


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    status = db.Column(db.String(50), default='Order Confirmed', nullable=False)
    transformer_model = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    dispatch_location = db.Column(db.String(255), default='Ropar Manufacturing Works')
    carrier_details = db.Column(db.String(200), nullable=True)
    tracking_reference = db.Column(db.String(100), nullable=True)
    estimated_delivery = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    invoices = db.relationship('Invoice', backref='order', lazy='dynamic')

    @property
    def equipment_model(self):
        return self.transformer_model

    @equipment_model.setter
    def equipment_model(self, val):
        self.transformer_model = val

    @property
    def production_stage(self):
        return self.status

    @production_stage.setter
    def production_stage(self, val):
        self.status = val

    @property
    def po_number(self):
        return self.tracking_reference or 'PO-CONFIRMED'

    @po_number.setter
    def po_number(self, val):
        self.tracking_reference = val


class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    taxable_amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    pdf_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='Issued', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def payment_status(self):
        return self.status

    @property
    def amount(self):
        return self.taxable_amount


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')
    link_url = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
