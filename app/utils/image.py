import cloudinary
import cloudinary.uploader
from flask import current_app
from typing import Dict, Optional, Tuple
from PIL import Image
import io
import base64

def init_cloudinary():
    """Initialize Cloudinary with credentials from config."""
    cloudinary.config(
        cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=current_app.config['CLOUDINARY_API_KEY'],
        api_secret=current_app.config['CLOUDINARY_API_SECRET']
    )

def resize_image(image_data: bytes, max_size: Tuple[int, int] = (800, 800)) -> bytes:
    """
    Resize an image while maintaining aspect ratio.
    
    Args:
        image_data (bytes): Raw image data
        max_size (tuple): Maximum width and height
    
    Returns:
        bytes: Resized image data
    """
    img = Image.open(io.BytesIO(image_data))
    img.thumbnail(max_size, Image.LANCZOS)
    
    # Convert back to bytes
    output = io.BytesIO()
    img.save(output, format=img.format or 'JPEG')
    return output.getvalue()

def upload_image(
    image_data: bytes,
    folder: str = "spaces",
    public_id: Optional[str] = None,
    tags: Optional[list] = None
) -> Dict:
    """
    Upload an image to Cloudinary.
    
    Args:
        image_data (bytes): Raw image data
        folder (str): Cloudinary folder to store the image
        public_id (str, optional): Custom public ID for the image
        tags (list, optional): List of tags for the image
    
    Returns:
        dict: Cloudinary upload response
    """
    try:
        # Initialize Cloudinary
        init_cloudinary()
        
        # Resize image before upload
        resized_image = resize_image(image_data)
        
        # Convert to base64
        base64_image = base64.b64encode(resized_image).decode('utf-8')
        
        # Upload to Cloudinary
        upload_params = {
            "folder": folder,
            "resource_type": "image",
            "tags": tags
        }
        
        if public_id:
            upload_params["public_id"] = public_id
            
        response = cloudinary.uploader.upload(
            f"data:image/jpeg;base64,{base64_image}",
            **upload_params
        )
        
        return {
            "url": response["secure_url"],
            "public_id": response["public_id"],
            "format": response["format"],
            "width": response["width"],
            "height": response["height"]
        }
    except Exception as e:
        current_app.logger.error(f"Failed to upload image to Cloudinary: {str(e)}")
        raise

def delete_image(public_id: str) -> bool:
    """
    Delete an image from Cloudinary.
    
    Args:
        public_id (str): Public ID of the image to delete
    
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        # Initialize Cloudinary
        init_cloudinary()
        
        response = cloudinary.uploader.destroy(public_id)
        return response["result"] == "ok"
    except Exception as e:
        current_app.logger.error(f"Failed to delete image from Cloudinary: {str(e)}")
        return False

def generate_transformation_url(url: str, width: int = 800, height: int = 800, crop: str = 'fill') -> str:
    """
    Generate a Cloudinary URL with transformations.
    
    Args:
        url (str): Original Cloudinary URL
        width (int): Desired width
        height (int): Desired height
        crop (str): Crop mode ('fill', 'fit', 'crop', etc.)
    
    Returns:
        str: Transformed URL
    """
    try:
        # Split URL to insert transformation
        parts = url.split('/upload/')
        if len(parts) != 2:
            return url
            
        transform = f"w_{width},h_{height},c_{crop}"
        return f"{parts[0]}/upload/{transform}/{parts[1]}"
    except Exception:
        return url 