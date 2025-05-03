import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Role

app = create_app()
app.app_context().push()

def add_role_to_user(email, role_name):
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"User with email {email} not found.")
        return
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name)
        db.session.add(role)
        db.session.commit()
        print(f"Role '{role_name}' created.")
    if role not in user.roles:
        user.roles.append(role)
        db.session.commit()
        print(f"Role '{role_name}' added to user {email}.")
    else:
        print(f"User {email} already has role '{role_name}'.")

if __name__ == "__main__":
    add_role_to_user("testuser@example.com", "space_owner")
