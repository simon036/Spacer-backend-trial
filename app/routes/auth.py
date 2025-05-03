from flask_restx import Namespace, Resource, fields
from flask import request, url_for
from app import db
from app.models import User, SocialAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.utils.sptp_utils import send_email
from datetime import datetime, timedelta
import uuid
import requests
from flask import current_app

api = Namespace('auth', description='Authentication related operations')

register_model = api.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'name': fields.String(description='User name'),
    'role': fields.String(description='User role', default='client')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

social_auth_model = api.model('SocialAuth', {
    'provider': fields.String(required=True, description='Social provider (google, facebook)'),
    'token': fields.String(required=True, description='Provider access token')
})

verify_email_model = api.model('VerifyEmail', {
    'token': fields.String(required=True, description='Verification token')
})

reset_password_model = api.model('ResetPassword', {
    'email': fields.String(required=True, description='User email')
})

new_password_model = api.model('NewPassword', {
    'token': fields.String(required=True, description='Reset token'),
    'password': fields.String(required=True, description='New password')
})

message_model = api.model('Message', {
    'message': fields.String(description='Response message')
})

token_model = api.model('Token', {
    'access_token': fields.String(description='JWT access token'),
    'is_verified': fields.Boolean(description='User verification status')
})

@api.route('/register')
class Register(Resource):
    @api.expect(register_model, validate=True)
    @api.marshal_with(message_model, code=201)
    def post(self):
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'client')

        if not email or not password:
            api.abort(400, 'Email and password are required')

        if User.query.filter_by(email=email).first():
            api.abort(409, 'User already exists')

        verification_token = str(uuid.uuid4())
        verification_expiry = datetime.utcnow() + timedelta(hours=24)

        hashed_password = generate_password_hash(password)
        new_user = User(
            email=email,
            password=hashed_password,
            name=name,
            verification_token=verification_token,
            verification_token_expiry=verification_expiry
        )
        db.session.add(new_user)
        db.session.commit()

        # Send verification email
        verification_url = f"{current_app.config['FRONTEND_URL']}/verify-email?token={verification_token}"
        send_email(
            to_email=email,
            subject="Verify your Spacer account",
            html_content=f"""
                <p>Hi {name or email},</p>
                <p>Thank you for registering on Spacer platform.</p>
                <p>Please click the following link to verify your email:</p>
                <p><a href="{verification_url}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
            """
        )

        return {'message': 'User registered successfully. Please check your email for verification.'}, 201

@api.route('/verify-email')
class VerifyEmail(Resource):
    @api.expect(verify_email_model, validate=True)
    @api.marshal_with(message_model)
    def post(self):
        token = request.json.get('token')
        if not token:
            api.abort(400, 'Verification token is required')

        user = User.query.filter_by(verification_token=token).first()
        if not user:
            api.abort(404, 'Invalid verification token')

        if user.verification_token_expiry < datetime.utcnow():
            api.abort(400, 'Verification token has expired')

        user.is_verified = True
        user.verification_token = None
        user.verification_token_expiry = None
        db.session.commit()

        return {'message': 'Email verified successfully'}, 200

@api.route('/login')
class Login(Resource):
    @api.expect(login_model, validate=True)
    @api.marshal_with(token_model)
    def post(self):
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            api.abort(400, 'Email and password are required')

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            api.abort(401, 'Invalid credentials')

        if not user.is_verified:
            api.abort(403, 'Please verify your email first')

        roles = [role.name for role in user.roles]
        additional_claims = {'roles': roles}
        access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
        return {'access_token': access_token, 'is_verified': user.is_verified}, 200

@api.route('/social-auth')
class SocialAuth(Resource):
    @api.expect(social_auth_model, validate=True)
    @api.marshal_with(token_model)
    def post(self):
        data = request.json
        provider = data.get('provider')
        token = data.get('token')

        if not provider or not token:
            api.abort(400, 'Provider and token are required')

        # Get user info from provider
        user_info = get_social_user_info(provider, token)
        if not user_info:
            api.abort(400, 'Invalid social token')

        # Check if user exists
        social_auth = SocialAuth.query.filter_by(
            provider=provider,
            provider_id=user_info['id']
        ).first()

        if social_auth:
            user = social_auth.user
        else:
            # Create new user
            user = User(
                email=user_info['email'],
                name=user_info.get('name'),
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()

            # Create social auth record
            social_auth = SocialAuth(
                user_id=user.id,
                provider=provider,
                provider_id=user_info['id']
            )
            db.session.add(social_auth)
            db.session.commit()

        roles = [role.name for role in user.roles]
        additional_claims = {'roles': roles}
        access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
        return {'access_token': access_token, 'is_verified': user.is_verified}, 200

@api.route('/reset-password')
class ResetPassword(Resource):
    @api.expect(reset_password_model, validate=True)
    @api.marshal_with(message_model)
    def post(self):
        email = request.json.get('email')
        if not email:
            api.abort(400, 'Email is required')

        user = User.query.filter_by(email=email).first()
        if not user:
            api.abort(404, 'User not found')

        reset_token = str(uuid.uuid4())
        reset_expiry = datetime.utcnow() + timedelta(hours=1)

        user.reset_token = reset_token
        user.reset_token_expiry = reset_expiry
        db.session.commit()

        reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={reset_token}"
        send_email(
            to_email=email,
            subject="Reset your Spacer password",
            html_content=f"""
                <p>Hi {user.name or email},</p>
                <p>You requested to reset your password.</p>
                <p>Click the following link to reset your password:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
            """
        )

        return {'message': 'Password reset email sent'}, 200

@api.route('/new-password')
class NewPassword(Resource):
    @api.expect(new_password_model, validate=True)
    @api.marshal_with(message_model)
    def post(self):
        token = request.json.get('token')
        password = request.json.get('password')

        if not token or not password:
            api.abort(400, 'Token and password are required')

        user = User.query.filter_by(reset_token=token).first()
        if not user:
            api.abort(404, 'Invalid reset token')

        if user.reset_token_expiry < datetime.utcnow():
            api.abort(400, 'Reset token has expired')

        user.password = generate_password_hash(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        return {'message': 'Password reset successfully'}, 200

@api.route('/protected')
class Protected(Resource):
    @jwt_required()
    @api.marshal_with(message_model)
    def get(self):
        current_user_id = get_jwt_identity()
        return {'message': f'Hello user {current_user_id}, you are authenticated'}, 200

def get_social_user_info(provider, token):
    if provider == 'google':
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.status_code == 200:
            data = response.json()
            return {
                'id': data['sub'],
                'email': data['email'],
                'name': data.get('name')
            }
    elif provider == 'facebook':
        response = requests.get(
            f'https://graph.facebook.com/me?fields=id,email,name&access_token={token}'
        )
        if response.status_code == 200:
            data = response.json()
            return {
                'id': data['id'],
                'email': data.get('email'),
                'name': data.get('name')
            }
    return None
