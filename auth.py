from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from models import db, User, DealerProfile, CustomerProfile, Notification

auth_bp = Blueprint('auth', __name__)

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Access restricted to authorized personnel only. Please sign in.', 'error')
            return redirect(url_for('auth.internal_login'))
        if not current_user.is_staff:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def dealer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'dealer':
            flash('This section is reserved for verified Gauri Power Dealers.', 'warning')
            return redirect(url_for('portal.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next') or request.form.get('next')
    if current_user.is_authenticated:
        if current_user.is_staff:
            return redirect(url_for('internal.dashboard'))
        return redirect(next_page or url_for('portal.dashboard'))

    if request.method == 'POST':
        login_as = (request.form.get('login_as') or request.form.get('role_hint') or 'end_customer').strip()
        identifier = (request.form.get('identifier') or request.form.get('email', '')).strip()
        password = request.form.get('password', '').strip()
        remember = bool(request.form.get('remember_me'))
        next_page = request.args.get('next') or request.form.get('next')

        if not identifier or not password:
            flash('Please enter your email or phone and password.', 'error')
            return render_template('auth/login.html', login_as=login_as, identifier=identifier, next_page=next_page)

        user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()

        if not user or not user.check_password(password):
            flash('Invalid login credentials. Please check your details and try again.', 'error')
            return render_template('auth/login.html', login_as=login_as, identifier=identifier, next_page=next_page)

        if user.is_staff:
            flash('Staff and administrators should sign in via the Authorized Personnel portal.', 'info')
            return redirect(url_for('auth.internal_login'))

        login_user(user, remember=remember)
        readable_role = user.role.replace('_', ' ').title()
        flash(f'Welcome back, {user.name} ({readable_role})!', 'success')
        return redirect(next_page or url_for('portal.dashboard'))

    default_role = request.args.get('role', 'end_customer')
    next_page = request.args.get('next', '')
    return render_template('auth/login.html', login_as=default_role, next_page=next_page)

@auth_bp.route('/internal/login', methods=['GET', 'POST'])
def internal_login():
    if current_user.is_authenticated and current_user.is_staff:
        return redirect(url_for('internal.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        remember = bool(request.form.get('remember_me'))

        user = User.query.filter_by(email=email).first()
        if not user or not user.is_staff or not user.check_password(password):
            flash('Invalid credentials for authorized staff login.', 'error')
            return render_template('auth/internal_login.html', email=email)

        login_user(user, remember=remember)
        flash(f'Authorized access granted: {user.name} ({user.role.title()})', 'success')
        return redirect(url_for('internal.dashboard'))

    return render_template('auth/internal_login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    next_page = request.args.get('next') or request.form.get('next')
    if current_user.is_authenticated:
        return redirect(next_page or url_for('public.home'))

    role = request.args.get('role', request.form.get('role', 'end_customer'))
    if role not in ['end_customer', 'dealer']:
        role = 'end_customer'

    if request.method == 'POST':
        role = request.form.get('role', 'end_customer')
        if role not in ['end_customer', 'dealer']:
            role = 'end_customer'

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        company_name = request.form.get('company_name', '').strip()
        
        # Address fields
        address_line = request.form.get('address_line', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        postal_code = request.form.get('postal_code', '').strip()
        country = request.form.get('country', 'India').strip() or 'India'
        
        # Extra fields
        gst_number = (request.form.get('gst_number') or request.form.get('gstin') or '').strip()
        industry_type = request.form.get('industry_type', '').strip()
        dealership_code = request.form.get('dealership_code', '').strip()
        territory = request.form.get('territory', '').strip()

        # Validation checks
        if not name or not email or not phone or not password or not company_name:
            flash('Please complete all required fields (Full Name, Email, Phone, Company Name, and Password).', 'error')
            return render_template('auth/register.html', role=role, form_data=request.form, next_page=next_page)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/register.html', role=role, form_data=request.form, next_page=next_page)

        if confirm_password and password != confirm_password:
            flash('Passwords do not match. Please verify and re-enter.', 'error')
            return render_template('auth/register.html', role=role, form_data=request.form, next_page=next_page)

        if User.query.filter_by(email=email).first():
            flash('An account with this email address already exists. Please sign in.', 'error')
            return render_template('auth/register.html', role=role, form_data=request.form, next_page=next_page)

        if User.query.filter_by(phone=phone).first():
            flash('An account with this mobile phone number already exists. Please sign in.', 'error')
            return render_template('auth/register.html', role=role, form_data=request.form, next_page=next_page)

        # Fallback defaults for address if not fully specified
        if not address_line:
            address_line = f"{company_name} Facility"
        if not city:
            city = "Ropar / Mohali"
        if not state:
            state = "Punjab"
        if not postal_code:
            postal_code = "140001"

        try:
            user = User(
                name=name,
                email=email,
                phone=phone,
                role=role
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            if role == 'dealer':
                dealer_profile = DealerProfile(
                    user_id=user.id,
                    company_name=company_name,
                    gst_number=gst_number,
                    dealership_code=dealership_code or None,
                    address_line=address_line,
                    city=city,
                    state=state,
                    postal_code=postal_code,
                    country=country,
                    territory=territory or f"{state} Region"
                )
                db.session.add(dealer_profile)
            else:
                cust_profile = CustomerProfile(
                    user_id=user.id,
                    company_name=company_name,
                    industry_type=industry_type or "General Manufacturing",
                    gst_number=gst_number,
                    address_line=address_line,
                    city=city,
                    state=state,
                    postal_code=postal_code,
                    country=country
                )
                db.session.add(cust_profile)

            welcome_note = Notification(
                user_id=user.id,
                title='Account Registered & Activated',
                message='Welcome to Gauri Power B2B Portal. You can now configure voltage stabilizers, submit RFQs, and track manufacturing milestones.',
                type='success',
                link_url='/products'
            )
            db.session.add(welcome_note)

            db.session.commit()
            login_user(user)
            flash(f'Account created successfully! Welcome to Gauri Power, {user.name}.', 'success')
            return redirect(next_page or url_for('public.home'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while creating your account: {str(e)}', 'error')
            return render_template('auth/register.html', role=role, form_data=request.form, next_page=next_page)

    return render_template('auth/register.html', role=role, form_data={}, next_page=next_page)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('public.home'))

@auth_bp.route('/forgot-password')
def forgot_password():
    return render_template('auth/forgot_password.html')
