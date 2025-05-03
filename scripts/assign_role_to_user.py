import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db
from app.models import User, Role

def assign_role_to_user(email, role_name):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"User with email {email} not found.")
            return
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            print(f"Role '{role_name}' not found. Creating it.")
            role = Role(name=role_name)
            db.session.add(role)
            db.session.commit()
        if role not in user.roles:
            user.roles.append(role)
            db.session.commit()
            print(f"Role '{role_name}' assigned to user {email}.")
        else:
            print(f"User {email} already has role '{role_name}'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python assign_role_to_user.py <email> <role_name>")
    else:
        email = sys.argv[1]
        role_name = sys.argv[2]
        assign_role_to_user(email, role_name)
