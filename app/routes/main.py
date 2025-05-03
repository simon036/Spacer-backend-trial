from flask_restx import Namespace, Resource

api = Namespace('main', description='Main related operations')

@api.route('/')
class Welcome(Resource):
    def get(self):
        """Welcome message"""
        return {'message': 'Welcome to the Spacer Platform Backend'}, 200
