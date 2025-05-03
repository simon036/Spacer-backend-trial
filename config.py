import os
from datetime import timedelta

def clean_env_value(value):
    """Clean environment variable value by removing comments"""
    if value is None:
        return None
    return str(value).split('#')[0].strip()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(clean_env_value(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', '3600'))))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(clean_env_value(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', '2592000'))))
    
    # Email settings
    MAIL_SERVER = os.environ.get('SMTP_SERVER')
    MAIL_PORT = int(clean_env_value(os.environ.get('SMTP_PORT', '587')))
    MAIL_USERNAME = os.environ.get('SMTP_USERNAME')
    MAIL_PASSWORD = os.environ.get('SENDINBLUE_API_KEY')
    MAIL_USE_TLS = clean_env_value(os.environ.get('SMTP_USE_TLS', 'True')).lower() == 'true'
    MAIL_DEFAULT_SENDER = os.environ.get('SMTP_FROM_EMAIL')
    
    # Cloudinary settings
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    # Frontend URL
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')
    GOOGLE_AUTH_ENDPOINT = os.environ.get('GOOGLE_AUTH_ENDPOINT')
    GOOGLE_TOKEN_ENDPOINT = os.environ.get('GOOGLE_TOKEN_ENDPOINT')
    GOOGLE_USERINFO_ENDPOINT = os.environ.get('GOOGLE_USERINFO_ENDPOINT')
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(clean_env_value(os.environ.get('MAX_CONTENT_LENGTH', '16777216')))
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Admin settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    
    # Payment settings
    PAYMENT_SIMULATION = clean_env_value(os.environ.get('PAYMENT_SIMULATION', 'true')).lower() == 'true'
    PAYMENT_SUCCESS_RATE = int(clean_env_value(os.environ.get('PAYMENT_SUCCESS_RATE', '100')))
    
    # Email verification settings
    EMAIL_VERIFICATION_EXPIRY = int(clean_env_value(os.environ.get('EMAIL_VERIFICATION_EXPIRY', '86400')))
    PASSWORD_RESET_EXPIRY = int(clean_env_value(os.environ.get('PASSWORD_RESET_EXPIRY', '3600'))) 