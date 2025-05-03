from flask_restx import Namespace, Resource, fields
from flask import request
from app.models import User
from app.utils.sptp_utils import send_email
from random import randint
from datetime import datetime, timedelta

api = Namespace('auth_2fa', description='Two-factor authentication operations')

otp_store = {}  # In-memory store for OTPs: {email: (otp, expiry_datetime)}

otp_model = api.model('OTP', {
    'email': fields.String(required=True, description='User email'),
})

verify_model = api.model('VerifyOTP', {
    'email': fields.String(required=True, description='User email'),
    'otp': fields.String(required=True, description='One-time password'),
})

@api.route('/send-otp')
class SendOTP(Resource):
    @api.expect(otp_model, validate=True)
    def post(self):
        data = request.json
        email = data.get('email')
        if not email:
            api.abort(400, 'Email is required')

        user = User.query.filter_by(email=email).first()
        if not user:
            api.abort(404, 'User not found')

        otp = str(randint(100000, 999999))
        expiry = datetime.utcnow() + timedelta(minutes=5)
        otp_store[email] = (otp, expiry)

        send_email(
            to_email=email,
            subject='Your OTP Code',
            html_content=f'<p>Your OTP code is: <strong>{otp}</strong></p><p>It expires in 5 minutes.</p>'
        )

        return {'message': 'OTP sent successfully'}, 200

@api.route('/verify-otp')
class VerifyOTP(Resource):
    @api.expect(verify_model, validate=True)
    def post(self):
        data = request.json
        email = data.get('email')
        otp = data.get('otp')

        if not email or not otp:
            api.abort(400, 'Email and OTP are required')

        stored_otp, expiry = otp_store.get(email, (None, None))
        if not stored_otp or datetime.utcnow() > expiry:
            api.abort(400, 'OTP expired or not found')

        if otp != stored_otp:
            api.abort(401, 'Invalid OTP')

        # OTP verified, remove from store
        otp_store.pop(email, None)

        return {'message': 'OTP verified successfully'}, 200
