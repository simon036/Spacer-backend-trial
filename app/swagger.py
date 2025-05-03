from flask_restx import Api

authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Type in the *\'Value\'* input box below: **\'Bearer &lt;JWT&gt;\'**, where JWT is the token'
    }
}

api = Api(
    title='Spacer API',
    version='1.0',
    description='A platform for booking and managing spaces',
    authorizations=authorizations,
    security='Bearer'
)

# Import all namespaces
from app.routes.auth import api as auth_ns
from app.routes.spaces import api as spaces_ns
from app.routes.bookings import api as bookings_ns
from app.routes.testimonials import api as testimonials_ns
from app.routes.admin import api as admin_ns
from app.routes.google_auth import api as google_auth_ns

# Add namespaces
api.add_namespace(auth_ns, path='/api/auth')
api.add_namespace(spaces_ns, path='/api/spaces')
api.add_namespace(bookings_ns, path='/api/bookings')
api.add_namespace(testimonials_ns, path='/api/testimonials')
api.add_namespace(admin_ns, path='/api/admin')
api.add_namespace(google_auth_ns, path='/api/auth') 