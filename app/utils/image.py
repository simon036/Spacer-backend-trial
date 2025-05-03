import cloudinary
import cloudinary.uploader
import cloudinary.api
from PIL import Image
import io
import base64
from flask import current_app
from typing import Dict, Optional, Tuple

def configure_cloudinary():
    """Initialize Cloudinary with credentials from config."""
    cloudinary.config(
        cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=current_app.config['CLOUDINARY_API_KEY'],
        api_secret=current_app.config['CLOUDINARY_API_SECRET']
    )

def resize_image(image_data: str, max_width: int = 800, max_height: int = 600) -> bytes:
    """
    Resize image before upload to optimize storage and performance.
    
    Args:
        image_data: Base64 encoded image data
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        
    Returns:
        Resized image as bytes
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Calculate new dimensions while maintaining aspect ratio
        width, height = image.size
        if width > max_width or height > max_height:
            ratio = min(max_width/width, max_height/height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to JPEG and save to bytes
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85)
        return output.getvalue()
    except Exception as e:
        current_app.logger.error(f"Error resizing image: {str(e)}")
        raise

def upload_image(image_data: str, folder: str = 'spaces', public_id: Optional[str] = None) -> str:
    """
    Upload image to Cloudinary with resizing.
    
    Args:
        image_data: Base64 encoded image data
        folder: Cloudinary folder to store the image
        public_id: Optional public ID for the image
        
    Returns:
        Secure URL of the uploaded image
    """
    configure_cloudinary()
    
    try:
        # Resize image before upload
        resized_image = resize_image(image_data)
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            resized_image,
            folder=folder,
            public_id=public_id,
            resource_type='image',
            format='jpg'
        )
        
        return upload_result['secure_url']
    except Exception as e:
        current_app.logger.error(f"Error uploading image to Cloudinary: {str(e)}")
        raise

def delete_image(public_id: str) -> Dict:
    """
    Delete image from Cloudinary.
    
    Args:
        public_id: Cloudinary public ID of the image
        
    Returns:
        Cloudinary deletion result
    """
    configure_cloudinary()
    
    try:
        return cloudinary.uploader.destroy(public_id)
    except Exception as e:
        current_app.logger.error(f"Error deleting image from Cloudinary: {str(e)}")
        raise

def get_image_url(public_id: str, transformations: Optional[Dict] = None) -> str:
    """
    Get Cloudinary URL with optional transformations.
    
    Args:
        public_id: Cloudinary public ID of the image
        transformations: Optional transformation parameters
        
    Returns:
        Transformed image URL
    """
    configure_cloudinary()
    
    try:
        return cloudinary.CloudinaryImage(public_id).build_url(transformation=transformations)
    except Exception as e:
        current_app.logger.error(f"Error generating image URL: {str(e)}")
        raise 