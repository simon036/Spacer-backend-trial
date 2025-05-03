import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_cors import CORS
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
api = Api(version='1.0', title='Spacer API', description='API documentation for Spacer backend', authorizations=authorizations, security='Bearer Auth')
mail = Mail()

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

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    api.init_app(app)

    @app.route('/test-db')
    def test_db():
        try:
            db.session.execute('SELECT 1')
            return "Database connection successful"
        except Exception as e:
            return f"Database connection failed: {e}"

    from app.routes.main import api as main_api
    api.add_namespace(main_api, path='/api')

    from app.routes.testimonials import api as testimonials_api
    api.add_namespace(testimonials_api, path='/api/testimonials')

    from app.routes.auth import api as auth_api
    api.add_namespace(auth_api, path='/api/auth')

    from app.routes.auth_2fa import api as auth_2fa_api
    api.add_namespace(auth_2fa_api, path='/api/auth_2fa')

    from app.routes.spaces import api as spaces_api
    api.add_namespace(spaces_api, path='/api/spaces')

    from app.routes.bookings import api as bookings_api
    api.add_namespace(bookings_api, path='/api/bookings')

    from app.routes.admin import api as admin_api
    api.add_namespace(admin_api, path='/api/admin')

    from app.routes.google_auth import api as google_auth_api
    api.add_namespace(google_auth_api, path='/api/auth')

    @app.route('/docs')
    def swagger_ui():
        return api.render_doc()

    return app
