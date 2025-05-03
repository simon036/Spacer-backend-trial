import unittest
import json
from app import create_app, db

class APITestCase(unittest.TestCase):
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

    def test_register_user(self):
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123"
        }
        response = self.client.post('/api/auth/register', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_login_user(self):
        # First register user
        self.test_register_user()
        data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        response = self.client.post('/api/auth/login', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn('access_token', json_data)

    def test_create_booking(self):
        # This test assumes user and space exist
        # You may need to create them or mock them here
        pass

if __name__ == '__main__':
    unittest.main()
