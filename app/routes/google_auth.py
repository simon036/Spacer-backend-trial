from flask import redirect, request, current_app
from flask_restx import Namespace, Resource
from flask_jwt_extended import create_access_token, create_refresh_token
import requests
from app.models.user import User
from app import db

api = Namespace('google_auth', description='Google OAuth authentication operations')

@api.route('/google/login')
class GoogleLogin(Resource):
    def get(self):
        """Redirect to Google OAuth login page"""
        auth_url = (
            f"{current_app.config['GOOGLE_AUTH_ENDPOINT']}?"
            f"client_id={current_app.config['GOOGLE_CLIENT_ID']}&"
            f"redirect_uri={current_app.config['GOOGLE_REDIRECT_URI']}&"
            "response_type=code&"
            "scope=email profile&"
            "access_type=offline&"
            "prompt=consent"
        )
        return redirect(auth_url)

@api.route('/google/callback')
class GoogleCallback(Resource):
    def get(self):
        """Handle Google OAuth callback"""
        code = request.args.get('code')
        if not code:
            return {'error': 'Authorization code not provided'}, 400

        # Exchange code for tokens
        token_data = {
            'code': code,
            'client_id': current_app.config['GOOGLE_CLIENT_ID'],
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
            'redirect_uri': current_app.config['GOOGLE_REDIRECT_URI'],
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(current_app.config['GOOGLE_TOKEN_ENDPOINT'], data=token_data)
        token_info = response.json()
        
        if 'error' in token_info:
            return {'error': 'Failed to get access token'}, 400

        # Get user info
        headers = {'Authorization': f"Bearer {token_info['access_token']}"}
        user_info = requests.get(current_app.config['GOOGLE_USERINFO_ENDPOINT'], headers=headers).json()

        # Find or create user
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            user = User(
                email=user_info['email'],
                username=user_info['email'].split('@')[0],
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()

        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Redirect to frontend with tokens
        frontend_url = current_app.config['FRONTEND_URL']
        return redirect(
            f"{frontend_url}/auth/callback?"
            f"access_token={access_token}&"
            f"refresh_token={refresh_token}"
        ) 