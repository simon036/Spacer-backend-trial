import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

def create_test_user():
    email = "testuser@example.com"
    password = "password123"
    if User.query.filter_by(email=email).first():
        print("Test user already exists.")
        return
    user = User(email=email, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    print("Test user created successfully.")

if __name__ == "__main__":
    create_test_user()
