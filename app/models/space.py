from app import db
from datetime import datetime

class Space(db.Model):
    __tablename__ = 'spaces'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(255), nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    amenities = db.Column(db.JSON)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    images = db.relationship('SpaceImage', backref='space', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='space', lazy=True, cascade='all, delete-orphan')

    def __init__(self, owner_id, name, description, address, price_per_day, capacity, amenities=None):
        self.owner_id = owner_id
        self.name = name
        self.description = description
        self.address = address
        self.price_per_day = price_per_day
        self.capacity = capacity
        self.amenities = amenities or {}

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'price_per_day': self.price_per_day,
            'capacity': self.capacity,
            'amenities': self.amenities,
            'is_available': self.is_available,
            'images': [image.to_dict() for image in self.images],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Space {self.name}>'

class SpaceImage(db.Model):
    __tablename__ = 'space_images'

    id = db.Column(db.Integer, primary_key=True)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    public_id = db.Column(db.String(255), nullable=False)  # Cloudinary public ID
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, space_id, url, public_id, is_primary=False):
        self.space_id = space_id
        self.url = url
        self.public_id = public_id
        self.is_primary = is_primary

    def to_dict(self):
        return {
            'id': self.id,
            'space_id': self.space_id,
            'url': self.url,
            'public_id': self.public_id,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<SpaceImage {self.id}>' 