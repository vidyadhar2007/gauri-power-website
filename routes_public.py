from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from models import Product, db

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    featured_products = Product.query.filter_by(is_featured=True).all()
    if not featured_products:
        featured_products = Product.query.limit(6).all()
    all_products = Product.query.all()
    return render_template('index.html', featured_products=featured_products, all_products=all_products)

@public_bp.route('/about')
def about():
    return render_template('about.html')

@public_bp.route('/products')
def products():
    category = request.args.get('category')
    search = request.args.get('q', '').strip()

    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.short_description.ilike(f'%{search}%'))

    product_list = query.all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template('products.html', products=product_list, categories=categories, selected_category=category, search=search)

@public_bp.route('/products/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    related_products = Product.query.filter(Product.id != product.id, Product.category == product.category).limit(3).all()
    if not related_products:
        related_products = Product.query.filter(Product.id != product.id).limit(3).all()
    return render_template('product_detail.html', product=product, related_products=related_products)

@public_bp.route('/manufacturing')
def manufacturing():
    return render_template('manufacturing.html')

@public_bp.route('/quality')
def quality():
    return render_template('quality.html')

@public_bp.route('/projects')
def projects():
    return render_template('projects.html')

@public_bp.route('/certifications')
def certifications():
    return render_template('certifications.html')

@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        inquiry_type = request.form.get('inquiry_type', 'General Inquiry')
        message = request.form.get('message')

        # In production this sends an internal email / records sales inquiry
        flash(f'Thank you, {name}! Your {inquiry_type} has been received by Gauri Power team. We will get back to you shortly.', 'success')
        return redirect(url_for('public.contact'))

    return render_template('contact.html')

@public_bp.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@public_bp.route('/terms')
def terms():
    return render_template('terms.html')

@public_bp.route('/ai-assistant')
def ai_assistant():
    return render_template('ai_assistant.html')
