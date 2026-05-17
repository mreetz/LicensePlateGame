import getpass
import sys

from werkzeug.security import generate_password_hash

from app import app
from extensions import db
from models import User

if len(sys.argv) != 2:
    print("Usage:")
    print("PYTHONPATH=. python scripts/make_admin.py user@example.com")
    sys.exit(1)

email = sys.argv[1]

with app.app_context():
    user = User.query.filter_by(email=email).first()

    if not user:
        username = input("Username to create: ").strip()
        password = getpass.getpass("Password for new admin user: ")

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            is_admin=True,
            is_approved=True,
        )
        db.session.add(user)
        print(f"Created admin user: {email}")
    else:
        user.is_admin = True
        user.is_approved = True
        print(f"Promoted existing user: {email}")

    db.session.commit()
    print(f"is_admin={user.is_admin}")
    print(f"is_approved={user.is_approved}")