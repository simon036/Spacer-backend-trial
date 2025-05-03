import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User

app = create_app()
app.app_context().push()

def list_users():
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}")

if __name__ == "__main__":
    list_users()
