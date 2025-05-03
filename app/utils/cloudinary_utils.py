import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import current_app

def configure_cloudinary():
    cloudinary.config(
        cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key=current_app.config.get('CLOUDINARY_API_KEY'),
        api_secret=current_app.config.get('CLOUDINARY_API_SECRET')
    )
    # Debug print to verify environment variables are loaded
    print("Cloudinary API Key:", current_app.config.get('CLOUDINARY_API_KEY'))

def upload_image(file):
    configure_cloudinary()
    result = cloudinary.uploader.upload(file, transformation=[
        {'width': 800, 'height': 600, 'crop': 'limit'}
    ])
    return result.get('secure_url')
