import base64
import requests
from app import create_app, db
from app.models import Space, User

app = create_app()
app.app_context().push()

def add_space_with_image(name, price_per_hour, status, owner_email, image_path):
    user = User.query.filter_by(email=owner_email).first()
    if not user:
        print(f"User with email {owner_email} not found.")
        return

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        image_data = f"data:image/jpeg;base64,{encoded_string}"

    # Call the POST /spaces API with image data
    url = "http://localhost:5000/api/spaces"
    headers = {
        "Content-Type": "application/json",
        # Add authorization header if needed, e.g. "Authorization": "Bearer <token>"
    }
    payload = {
        "name": name,
        "price_per_hour": price_per_hour,
        "status": status,
        "image": image_data
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print("Space added successfully:", response.json())
    else:
        print("Failed to add space:", response.status_code, response.text)

if __name__ == "__main__":
    # Example usage
    add_space_with_image(
        name="Sample Space from Script",
        price_per_hour=60,
        status="available",
        owner_email="admin@spacer.com",
        image_path="path/to/your/image.jpg"
    )
