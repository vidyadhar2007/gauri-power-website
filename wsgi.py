import os
from app import create_app
from models import db, Product

app = create_app()

with app.app_context():
    db.create_all()
    if not Product.query.first():
        from seed_data import seed_database
        seed_database()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
