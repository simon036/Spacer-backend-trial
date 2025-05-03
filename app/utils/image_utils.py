import cloudinary
import cloudinary.uploader
import cloudinary.api
from PIL import Image
import io
from flask import current_app

def configure_cloudinary():
    cloudinary.config(
        cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=current_app.config['CLOUDINARY_API_KEY'],
        api_secret=current_app.config['CLOUDINARY_API_SECRET']
    )

def resize_image(image_data, max_size=(800, 800)):
    """
    Resize image while maintaining aspect ratio
    """
    img = Image.open(io.BytesIO(image_data))
    
    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background
    
    # Calculate new dimensions
    ratio = min(max_size[0] / img.size[0], max_size[1] / img.size[1])
    new_size = tuple(int(dim * ratio) for dim in img.size)
    
    # Resize image
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Save to bytes
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=85)
    return output.getvalue()

def upload_image(image_data, folder='spaces', public_id=None):
    """
    Upload image to Cloudinary with resizing
    """
    configure_cloudinary()
    
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

def delete_image(public_id):
    """
    Delete image from Cloudinary
    """
    configure_cloudinary()
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        current_app.logger.error(f"Error deleting image: {str(e)}")
        return False

def get_image_url(public_id, transformations=None):
    """
    Get Cloudinary URL with optional transformations
    """
    configure_cloudinary()
    return cloudinary.CloudinaryImage(public_id).build_url(transformation=transformations) 