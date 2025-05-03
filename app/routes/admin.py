from flask_restx import Namespace, Resource, fields
from flask import request
from app import db
from app.models import User, Role, Space, Booking, Testimonial
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace('admin', description='Admin related operations')

role_model = api.model('Role', {
    'id': fields.Integer(readonly=True, description='Role ID'),
    'name': fields.String(required=True, description='Role name')
})

user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='User ID'),
    'email': fields.String(required=True, description='User email'),
    'roles': fields.List(fields.String, description='List of role names')
})

space_model = api.model('Space', {
    'id': fields.Integer(readonly=True, description='Space ID'),
    'name': fields.String(required=True, description='Space name'),
    'price_per_hour': fields.Float(required=True, description='Price per hour'),
    'status': fields.String(description='Space status')
})

booking_model = api.model('Booking', {
    'id': fields.Integer(readonly=True, description='Booking ID'),
    'space_id': fields.Integer(required=True, description='Space ID'),
    'user_id': fields.Integer(required=True, description='User ID'),
    'start_time': fields.String(description='Start time as ISO string'),
    'end_time': fields.String(description='End time as ISO string'),
    'status': fields.String(description='Booking status')
})

testimonial_model = api.model('Testimonial', {
    'id': fields.Integer(readonly=True, description='Testimonial ID'),
    'user_name': fields.String(description='User name'),
    'content': fields.String(description='Testimonial content')
})

system_settings_model = api.model('SystemSettings', {
    'payment_options': fields.String(description='Payment options'),
    'notification_preferences': fields.String(description='Notification preferences'),
    'api_keys': fields.String(description='API keys')
})

def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not any(role.name == 'admin' for role in user.roles):
            api.abort(403, 'Admin access required')
        return fn(*args, **kwargs)
    return wrapper

@api.route('/users')
class UserList(Resource):
    @admin_required
    @api.marshal_list_with(user_model)
    def get(self):
        users = User.query.all()
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'email': user.email,
                'roles': [role.name for role in user.roles]
            })
        return result

    @admin_required
    def delete(self):
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            api.abort(400, 'user_id query parameter required')
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200

@api.route('/users/<int:user_id>/roles')
class UserRole(Resource):
    @admin_required
    @api.expect(api.model('UserRoleUpdate', {
        'role': fields.String(required=True, description='Role to assign or remove'),
        'action': fields.String(required=True, description='Action to perform: assign or remove')
    }))
    def post(self, user_id):
        data = request.json
        role_name = data.get('role')
        action = data.get('action')

        if action not in ['assign', 'remove']:
            api.abort(400, 'Invalid action')

        user = User.query.get_or_404(user_id)
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            api.abort(404, 'Role not found')

        if action == 'assign':
            if role not in user.roles:
                user.roles.append(role)
        elif action == 'remove':
            if role in user.roles:
                user.roles.remove(role)

        db.session.commit()
        return {'message': f'Role {action}ed successfully'}, 200

@api.route('/spaces')
class SpaceList(Resource):
    @admin_required
    @api.marshal_list_with(space_model)
    def get(self):
        spaces = Space.query.all()
        return spaces

    @admin_required
    @api.expect(space_model)
    def post(self):
        data = request.json
        name = data.get('name')
        price_per_hour = data.get('price_per_hour')
        status = data.get('status', 'available')

        if not name or price_per_hour is None:
            api.abort(400, 'Name and price_per_hour are required')

        new_space = Space(name=name, price_per_hour=price_per_hour, status=status)
        db.session.add(new_space)
        db.session.commit()
        return {'message': 'Space created successfully', 'space_id': new_space.id}, 201

@api.route('/spaces/<int:space_id>')
class SpaceResource(Resource):
    @admin_required
    @api.marshal_with(space_model)
    def get(self, space_id):
        space = Space.query.get_or_404(space_id)
        return space

    @admin_required
    @api.expect(space_model)
    def put(self, space_id):
        space = Space.query.get_or_404(space_id)
        data = request.json
        space.name = data.get('name', space.name)
        space.price_per_hour = data.get('price_per_hour', space.price_per_hour)
        space.status = data.get('status', space.status)
        db.session.commit()
        return {'message': 'Space updated successfully'}, 200

    @admin_required
    def delete(self, space_id):
        space = Space.query.get_or_404(space_id)
        db.session.delete(space)
        db.session.commit()
        return {'message': 'Space deleted successfully'}, 200

@api.route('/bookings')
class BookingList(Resource):
    @admin_required
    def get(self):
        bookings = Booking.query.all()
        result = []
        for booking in bookings:
            result.append({
                'id': booking.id,
                'space_id': booking.space_id,
                'user_id': booking.user_id,
                'start_time': booking.start_time.isoformat() if booking.start_time else None,
                'end_time': booking.end_time.isoformat() if booking.end_time else None,
                'status': booking.status
            })
        return result

    @admin_required
    @api.expect(api.model('BookingUpdate', {
        'status': fields.String(required=True, description='Booking status')
    }))
    def put(self):
        booking_id = request.args.get('booking_id', type=int)
        if not booking_id:
            api.abort(400, 'booking_id query parameter required')
        booking = Booking.query.get_or_404(booking_id)
        data = request.json
        booking.status = data.get('status', booking.status)
        db.session.commit()
        return {'message': 'Booking status updated successfully'}, 200

    @admin_required
    def delete(self):
        booking_id = request.args.get('booking_id', type=int)
        if not booking_id:
            api.abort(400, 'booking_id query parameter required')
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        return {'message': 'Booking deleted successfully'}, 200

@api.route('/testimonials')
class TestimonialList(Resource):
    @admin_required
    @api.marshal_list_with(testimonial_model)
    def get(self):
        testimonials = Testimonial.query.all()
        return testimonials

    @admin_required
    @api.expect(api.model('TestimonialUpdate', {
        'content': fields.String(required=True, description='Testimonial content')
    }))
    def put(self):
        testimonial_id = request.args.get('testimonial_id', type=int)
        if not testimonial_id:
            api.abort(400, 'testimonial_id query parameter required')
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        data = request.json
        testimonial.content = data.get('content', testimonial.content)
        db.session.commit()
        return {'message': 'Testimonial updated successfully'}, 200

    @admin_required
    def delete(self):
        testimonial_id = request.args.get('testimonial_id', type=int)
        if not testimonial_id:
            api.abort(400, 'testimonial_id query parameter required')
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        db.session.delete(testimonial)
        db.session.commit()
        return {'message': 'Testimonial deleted successfully'}, 200

@api.route('/roles')
class RoleList(Resource):
    @admin_required
    @api.marshal_list_with(role_model)
    def get(self):
        roles = Role.query.all()
        return roles

    @admin_required
    @api.expect(role_model)
    def post(self):
        data = request.json
        name = data.get('name')
        if not name:
            api.abort(400, 'Role name is required')
        if Role.query.filter_by(name=name).first():
            api.abort(409, 'Role already exists')
        new_role = Role(name=name)
        db.session.add(new_role)
        db.session.commit()
        return {'message': 'Role created successfully', 'role_id': new_role.id}, 201

    @admin_required
    @api.expect(role_model)
    def put(self):
        role_id = request.args.get('role_id', type=int)
        if not role_id:
            api.abort(400, 'role_id query parameter required')
        role = Role.query.get_or_404(role_id)
        data = request.json
        role.name = data.get('name', role.name)
        db.session.commit()
        return {'message': 'Role updated successfully'}, 200

    @admin_required
    def delete(self):
        role_id = request.args.get('role_id', type=int)
        if not role_id:
            api.abort(400, 'role_id query parameter required')
        role = Role.query.get_or_404(role_id)
        db.session.delete(role)
        db.session.commit()
        return {'message': 'Role deleted successfully'}, 200

@api.route('/system-settings')
class SystemSettings(Resource):
    @admin_required
    @api.marshal_with(system_settings_model)
    def get(self):
        # Placeholder for system settings retrieval
        return {
            'payment_options': 'Credit Card, PayPal',
            'notification_preferences': 'Email, SMS',
            'api_keys': '***'
        }

    @admin_required
    @api.expect(system_settings_model)
    def put(self):
        # Placeholder for system settings update
        data = request.json
        # Save settings logic here
        return {'message': 'System settings updated successfully'}, 200
