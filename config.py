import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gauri-power-secret-key-2026-industrial')
    
    is_vercel = os.environ.get('VERCEL') is not None
    if is_vercel:
        default_db = 'sqlite:////tmp/instance/gauripower.db'
        default_upload = '/tmp/uploads'
    else:
        default_db = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'gauripower.db')
        default_upload = os.path.join(BASE_DIR, 'static', 'uploads')

    _db_url = os.environ.get('DATABASE_URL', default_db)
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configurations
    UPLOAD_FOLDER = default_upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'dwg'}
    
    # Company details grounded in official catalogue
    COMPANY_NAME = 'Gauri Power'
    COMPANY_SHORT_NAME = 'Gauri Power'
    COMPANY_TAGLINE = 'We correct the Power...'
    COMPANY_WEBSITE = 'www.gauripower.in'
    COMPANY_EMAIL = 'Gauripower09@gmail.com'
    COMPANY_PHONES = ['+91-81789-80216', '+91-78149-43673']
    
    COMPANY_ADDRESS = {
        'title': 'Registered Office & Manufacturing Works',
        'address': 'Vill. Nanakpura, Opp J.J. Valley',
        'city': 'Ropar',
        'pincode': '140001',
        'state': 'Punjab',
        'country': 'India'
    }
    HEAD_OFFICE_ADDRESS = COMPANY_ADDRESS
    FACTORY_ADDRESS = COMPANY_ADDRESS
