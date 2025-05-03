from flask_restx import Namespace, Resource, fields
from flask import request
from app import db
from app.models import Space, User, SpaceImage
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.image_utils import upload_image, delete_image
from datetime import datetime

api = Namespace('spaces', description='Spaces related operations')

space_model = api.model('Space', {
    'id': fields.Integer(readonly=True, description='The space unique identifier'),
    'public_id': fields.String(readonly=True, description='Public identifier'),
    'name': fields.String(required=True, description='Space name'),
    'description': fields.String(description='Space description'),
    'price_per_hour': fields.Float(required=True, description='Price per hour'),
    'capacity': fields.Integer(description='Maximum capacity'),
    'amenities': fields.Raw(description='List of amenities'),
    'location': fields.String(description='Space location'),
    'status': fields.String(description='Space status', default='available'),
    'owner_id': fields.Integer(description='Owner user ID'),
    'created_at': fields.DateTime(readonly=True),
    'updated_at': fields.DateTime(readonly=True),
    'images': fields.List(fields.String, description='List of image URLs')
})

space_create_model = api.model('SpaceCreate', {
    'name': fields.String(required=True, description='Space name'),
    'description': fields.String(description='Space description'),
    'price_per_hour': fields.Float(required=True, description='Price per hour'),
    'capacity': fields.Integer(description='Maximum capacity'),
    'amenities': fields.Raw(description='List of amenities'),
    'location': fields.String(description='Space location'),
    'status': fields.String(description='Space status', default='available'),
    'images': fields.List(fields.String, description='List of base64 encoded images')
})

space_update_model = api.model('SpaceUpdate', {
    'name': fields.String(description='Space name'),
    'description': fields.String(description='Space description'),
    'price_per_hour': fields.Float(description='Price per hour'),
    'capacity': fields.Integer(description='Maximum capacity'),
    'amenities': fields.Raw(description='List of amenities'),
    'location': fields.String(description='Space location'),
    'status': fields.String(description='Space status'),
    'images': fields.List(fields.String, description='List of base64 encoded images')
})

@api.route('')
class SpaceList(Resource):
    @api.param('page', 'Page number')
    @api.param('per_page', 'Spaces per page')
    @api.param('status', 'Filter by status')
    @api.param('min_price', 'Minimum price per hour')
    @api.param('max_price', 'Maximum price per hour')
    @api.param('capacity', 'Minimum capacity')
    @api.param('location', 'Location filter')
    @api.marshal_list_with(space_model)
    def get(self):
        """List spaces with pagination and filters"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status', None)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        capacity = request.args.get('capacity', type=int)
        location = request.args.get('location')

        query = Space.query

        if status_filter:
            query = query.filter_by(status=status_filter)
        if min_price is not None:
            query = query.filter(Space.price_per_hour >= min_price)
        if max_price is not None:
            query = query.filter(Space.price_per_hour <= max_price)
        if capacity is not None:
            query = query.filter(Space.capacity >= capacity)
        if location:
            query = query.filter(Space.location.ilike(f'%{location}%'))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items

    @jwt_required()
    @api.expect(space_create_model, validate=True)
    @api.marshal_with(space_model, code=201)
    def post(self):
        """Add a new space"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not any(role.name in ['admin', 'space_owner'] for role in user.roles):
            api.abort(403, 'Unauthorized')

        data = request.json
        name = data.get('name')
        description = data.get('description')
        price_per_hour = data.get('price_per_hour')
        capacity = data.get('capacity')
        amenities = data.get('amenities')
        location = data.get('location')
        status = data.get('status', 'available')
        images = data.get('images', [])

        if not name or price_per_hour is None:
            api.abort(400, 'Name and price_per_hour are required')

        new_space = Space(
            name=name,
            description=description,
            price_per_hour=price_per_hour,
            capacity=capacity,
            amenities=amenities,
            location=location,
            status=status,
            owner_id=current_user_id
        )
        db.session.add(new_space)
        db.session.commit()

        # Upload images
        for i, image_data in enumerate(images):
            try:
                image_url = upload_image(image_data, folder=f'spaces/{new_space.public_id}')
                space_image = SpaceImage(
                    space_id=new_space.id,
                    image_url=image_url,
                    is_primary=(i == 0)
                )
                db.session.add(space_image)
            except Exception as e:
                api.abort(400, f'Error uploading image: {str(e)}')

        db.session.commit()
        return new_space, 201

@api.route('/<int:space_id>')
@api.param('space_id', 'The space identifier')
class SpaceResource(Resource):
    @api.marshal_with(space_model)
    def get(self, space_id):
        """Get space details by ID"""
        space = Space.query.get_or_404(space_id)
        return space

    @jwt_required()
    @api.expect(space_update_model)
    @api.marshal_with(space_model)
    def put(self, space_id):
        """Update space details"""
        current_user_id = get_jwt_identity()
        space = Space.query.get_or_404(space_id)

        if space.owner_id != current_user_id and not any(role.name == 'admin' for role in User.query.get(current_user_id).roles):
            api.abort(403, 'Unauthorized')

        data = request.json
        for field in ['name', 'description', 'price_per_hour', 'capacity', 'amenities', 'location', 'status']:
            if field in data:
                setattr(space, field, data[field])

        # Handle image updates
        if 'images' in data:
            # Delete existing images
            for image in space.images:
                try:
                    delete_image(image.image_url)
                except:
                    pass
                db.session.delete(image)

            # Upload new images
            for i, image_data in enumerate(data['images']):
                try:
                    image_url = upload_image(image_data, folder=f'spaces/{space.public_id}')
                    space_image = SpaceImage(
                        space_id=space.id,
                        image_url=image_url,
                        is_primary=(i == 0)
                    )
                    db.session.add(space_image)
                except Exception as e:
                    api.abort(400, f'Error uploading image: {str(e)}')

        db.session.commit()
        return space

    @jwt_required()
    @api.response(204, 'Space deleted')
    def delete(self, space_id):
        """Delete a space"""
        current_user_id = get_jwt_identity()
        space = Space.query.get_or_404(space_id)

        if space.owner_id != current_user_id and not any(role.name == 'admin' for role in User.query.get(current_user_id).roles):
            api.abort(403, 'Unauthorized')

        # Delete images from Cloudinary
        for image in space.images:
            try:
                delete_image(image.image_url)
            except:
                pass

        db.session.delete(space)
        db.session.commit()
        return '', 204
