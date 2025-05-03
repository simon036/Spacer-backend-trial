from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Testimonial
from app import db

api = Namespace('testimonials', description='Testimonials operations')

@api.route('/')
class TestimonialList(Resource):
    @api.doc('list_testimonials')
    def get(self):
        """List all testimonials"""
        testimonials = Testimonial.query.all()
        return [testimonial.to_dict() for testimonial in testimonials]

    @api.doc('create_testimonial')
    @jwt_required()
    def post(self):
        """Create a new testimonial"""
        data = request.get_json()
        user_id = get_jwt_identity()
        
        testimonial = Testimonial(
            user_id=user_id,
            content=data['content'],
            rating=data['rating']
        )
        
        db.session.add(testimonial)
        db.session.commit()
        
        return testimonial.to_dict(), 201

@api.route('/<int:id>')
class TestimonialResource(Resource):
    @api.doc('get_testimonial')
    def get(self, id):
        """Get a testimonial by ID"""
        testimonial = Testimonial.query.get_or_404(id)
        return testimonial.to_dict()

    @api.doc('update_testimonial')
    @jwt_required()
    def put(self, id):
        """Update a testimonial"""
        testimonial = Testimonial.query.get_or_404(id)
        user_id = get_jwt_identity()
        
        if testimonial.user_id != user_id:
            return {'error': 'Unauthorized'}, 403
            
        data = request.get_json()
        testimonial.content = data.get('content', testimonial.content)
        testimonial.rating = data.get('rating', testimonial.rating)
        
        db.session.commit()
        return testimonial.to_dict()

    @api.doc('delete_testimonial')
    @jwt_required()
    def delete(self, id):
        """Delete a testimonial"""
        testimonial = Testimonial.query.get_or_404(id)
        user_id = get_jwt_identity()
        
        if testimonial.user_id != user_id:
            return {'error': 'Unauthorized'}, 403
            
        db.session.delete(testimonial)
        db.session.commit()
        return '', 204
