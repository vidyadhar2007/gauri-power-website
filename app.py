import os
from datetime import datetime, timezone
from flask import Flask, render_template
from flask_login import LoginManager, current_user
from config import Config
from models import db, User, Notification

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        if not os.environ.get('VERCEL'):
            os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
    except Exception:
        pass

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this portal section.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes_public import public_bp
    from auth import auth_bp
    from routes_quotation import quotation_bp
    from routes_portal import portal_bp
    from routes_internal import internal_bp
    from routes_api import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(quotation_bp)
    app.register_blueprint(portal_bp)
    app.register_blueprint(internal_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_global_data():
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()

        return {
            'now': datetime.now(timezone.utc),
            'current_year': datetime.now().year,
            'company_name': app.config['COMPANY_NAME'],
            'company_short_name': app.config['COMPANY_SHORT_NAME'],
            'company_tagline': app.config['COMPANY_TAGLINE'],
            'company_website': app.config['COMPANY_WEBSITE'],
            'company_email': app.config['COMPANY_EMAIL'],
            'company_phones': app.config['COMPANY_PHONES'],
            'head_office': app.config['HEAD_OFFICE_ADDRESS'],
            'factory_address': app.config['FACTORY_ADDRESS'],
            'unread_notifications_count': unread_count
        }

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
