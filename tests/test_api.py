import unittest
import json
from app import create_app, db
from app.models import User, Space

class SpacerBackendTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_registration_and_login(self):
        # Register user
        response = self.client.post('/api/auth/register', json={
            'email': 'testuser@example.com',
            'password': 'password123',
            'role': 'client'
        })
        self.assertEqual(response.status_code, 201)

        # Login user
        response = self.client.post('/api/auth/login', json={
            'email': 'testuser@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)

    def test_add_and_list_spaces(self):
        # Register and login user with space_owner role
        self.client.post('/api/auth/register', json={
            'email': 'owner@example.com',
            'password': 'password123',
            'role': 'space_owner'
        })
        login_resp = self.client.post('/api/auth/login', json={
            'email': 'owner@example.com',
            'password': 'password123'
        })
        token = json.loads(login_resp.data)['access_token']

        # Add space
        response = self.client.post('/api/spaces', data={
            'name': 'Test Space',
            'price_per_hour': 50
        }, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 201)

        # List spaces
        response = self.client.get('/api/spaces')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(len(data['spaces']) > 0)

if __name__ == '__main__':
    unittest.main()
