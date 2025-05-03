import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask_mail import Mail
from config import Config

load_dotenv()  # Load environment variables from .env file

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Add a JWT with ** Bearer <JWT> **"
    }
}

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = Api(
    version='1.0',
    title='Spacer API',
    description='API documentation for Spacer backend',
    authorizations=authorizations,
    security='Bearer Auth',
    doc='/api/v1/docs'  # Versioned documentation URL
)
mail = Mail()
limiter = Limiter(key_func=get_remote_address)

def create_app(test_config=None):
    app = Flask(__name__)
    if test_config is None:
        app.config.from_object('app.config.Config')
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret')
        app.config['CLOUDINARY_CLOUD_NAME'] = os.getenv('CLOUDINARY_CLOUD_NAME')
        app.config['CLOUDINARY_API_KEY'] = os.getenv('CLOUDINARY_API_KEY')
        app.config['CLOUDINARY_API_SECRET'] = os.getenv('CLOUDINARY_API_SECRET')
        app.config['JWT_ENCODE_ALGORITHM'] = 'HS256'
    else:
        app.config.update(test_config)

    # Enhanced CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    api.init_app(app)
    limiter.init_app(app)

    # Rate limit configuration
    limiter.limit("200 per day")(app)
    limiter.limit("50 per hour")(app)
    limiter.limit("20 per minute")(app)

    @app.route('/test-db')
    def test_db():
        try:
            db.session.execute('SELECT 1')
            return "Database connection successful"
        except Exception as e:
            return f"Database connection failed: {e}"

    # Versioned API routes
    from app.routes.main import api as main_api
    api.add_namespace(main_api, path='/api/v1')

    from app.routes.testimonials import api as testimonials_api
    api.add_namespace(testimonials_api, path='/api/v1/testimonials')

    from app.routes.auth import api as auth_api
    api.add_namespace(auth_api, path='/api/v1/auth')

    from app.routes.auth_2fa import api as auth_2fa_api
    api.add_namespace(auth_2fa_api, path='/api/v1/auth_2fa')

    from app.routes.spaces import api as spaces_api
    api.add_namespace(spaces_api, path='/api/v1/spaces')

    from app.routes.bookings import api as bookings_api
    api.add_namespace(bookings_api, path='/api/v1/bookings')

    from app.routes.admin import api as admin_api
    api.add_namespace(admin_api, path='/api/v1/admin')

    from app.routes.google_auth import api as google_auth_api
    api.add_namespace(google_auth_api, path='/api/v1/auth')

    @app.route('/docs')
    def swagger_ui():
        return api.render_doc()

    # Global error handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        return {
            'error': 'Bad Request',
            'message': str(error),
            'status_code': 400
        }, 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return {
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource',
            'status_code': 401
        }, 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return {
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'status_code': 403
        }, 403

    @app.errorhandler(404)
    def not_found_error(error):
        return {
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }, 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return {
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for the requested URL',
            'status_code': 405
        }, 405

    @app.errorhandler(429)
    def too_many_requests_error(error):
        return {
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded',
            'status_code': 429
        }, 429

    @app.errorhandler(500)
    def internal_server_error(error):
        return {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }, 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f"Unhandled exception: {str(error)}")
        return {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }, 500

    return app
