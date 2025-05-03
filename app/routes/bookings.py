from flask_restx import Namespace, Resource, fields
from flask import request
from app import db
from app.models import Booking, Space, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.utils.sendgrid_utils import send_email

api = Namespace('bookings', description='Bookings related operations')

booking_model = api.model('Booking', {
    'id': fields.Integer(readonly=True, description='The booking unique identifier'),
    'user_id': fields.Integer(description='User ID who made the booking'),
    'space_id': fields.Integer(required=True, description='Space ID'),
    'start_time': fields.DateTime(required=True, description='Booking start time'),
    'end_time': fields.DateTime(required=True, description='Booking end time'),
    'total_cost': fields.Float(description='Total cost of the booking'),
    'status': fields.String(description='Booking status')
})

booking_create_model = api.model('BookingCreate', {
    'space_id': fields.Integer(required=True, description='Space ID'),
    'start_time': fields.String(required=True, description='Booking start time in ISO format'),
    'end_time': fields.String(required=True, description='Booking end time in ISO format')
})

@api.route('')
class BookingList(Resource):
    @jwt_required()
    @api.expect(booking_create_model, validate=True)
    def post(self):
        """Create a new booking"""
        current_user_id = get_jwt_identity()
        data = request.json

        space_id = data.get('space_id')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')

        if not space_id or not start_time_str or not end_time_str:
            api.abort(400, 'space_id, start_time, and end_time are required')

        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
        except ValueError:
            api.abort(400, 'Invalid date format. Use ISO format.')

        if start_time >= end_time:
            api.abort(400, 'start_time must be before end_time')

        space = Space.query.get(space_id)
        if not space or space.status != 'available':
            api.abort(400, 'Space not available')

        duration_hours = (end_time - start_time).total_seconds() / 3600
        total_cost = duration_hours * space.price_per_hour

        new_booking = Booking(
            user_id=current_user_id,
            space_id=space_id,
            start_time=start_time,
            end_time=end_time,
            total_cost=total_cost,
            status='pending'
        )
        db.session.add(new_booking)
        db.session.commit()

        # Optionally update space status to 'booked'
        space.status = 'booked'
        db.session.commit()

        # Send booking confirmation email
        user = User.query.get(current_user_id)
        if user:
            send_email(
                to_email=user.email,
                subject="Booking Confirmation",
                html_content=f"<p>Dear {user.email},</p><p>Your booking for space '{space.name}' from {start_time} to {end_time} has been confirmed.</p>"
            )

        return {'message': 'Booking created successfully', 'booking_id': new_booking.id}, 201

@api.route('/<int:booking_id>')
@api.param('booking_id', 'The booking identifier')
class BookingResource(Resource):
    @jwt_required()
    @api.marshal_with(booking_model)
    def get(self, booking_id):
        """Get booking details by ID"""
        current_user_id = get_jwt_identity()
        booking = Booking.query.get_or_404(booking_id)

        user = User.query.get(current_user_id)
        if booking.user_id != current_user_id and (not user or not any(role.name == 'admin' for role in user.roles)):
            api.abort(403, 'Unauthorized')

        return booking
