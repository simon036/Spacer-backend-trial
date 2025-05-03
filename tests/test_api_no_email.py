import unittest
import json
from app import create_app, db

class APINoEmailTestCase(unittest.TestCase):
    def setUp(self):
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_spaces(self):
        response = self.client.get('/api/spaces')
        self.assertEqual(response.status_code, 200)

    def test_login_user(self):
        # Create user directly in DB to avoid registration email
        with self.app.app_context():
            from app.models import User
            from werkzeug.security import generate_password_hash
            user = User(email='testuser@example.com', password=generate_password_hash('password123'))
            db.session.add(user)
            db.session.commit()

        data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        # Set JWT_SECRET_KEY in headers for test client
        with self.app.test_request_context():
            self.app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'
        response = self.client.post('/api/auth/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('access_token', json_data)

if __name__ == '__main__':
    unittest.main()
