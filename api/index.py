import os
import sys
import shutil

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# On Vercel serverless environment, setup database in /tmp
if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
    try:
        src_db = os.path.join(root_dir, "instance", "gauripower.db")
        dst_db = "/tmp/gauripower.db"
        if os.path.exists(src_db) and not os.path.exists(dst_db):
            shutil.copyfile(src_db, dst_db)
    except Exception as e:
        print(f"Error copying database to /tmp: {e}")

from app import create_app
from models import db, Product

app = create_app()

with app.app_context():
    try:
        db.create_all()
        if not Product.query.first():
            from seed_data import seed_database
            seed_database(app)
    except Exception as e:
        print(f"App initialization note: {e}")

# Expose app for Vercel WSGI
application = app
