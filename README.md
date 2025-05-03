# Spacer Backend

A Flask-based backend for the Spacer platform, which connects space owners with people looking for unique spaces to meet, create, and celebrate.

## Features

- JWT Authentication with 2-step verification
- Social Authentication (Google, Facebook)
- Role-based access control
- Space management with image uploads
- Booking system with payment simulation
- Email notifications using Sendinblue
- Cloudinary image storage
- Swagger API documentation
- Rate limiting and caching
- Comprehensive error handling
- Data validation and pagination

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (optional, for rate limiting and caching)
- Cloudinary account
- Sendinblue account
- Google OAuth credentials
- Facebook OAuth credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/spacer-backend.git
cd spacer-backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `env.example` and fill in your credentials:
```bash
cp env.example .env
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the development server:
```bash
flask run
```

## API Documentation

The API documentation is available at `/api/docs` when running the server. Here's a summary of the main endpoints:

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login with email and password
- `POST /api/auth/social-auth` - Login with social providers
- `POST /api/auth/verify-email` - Verify email address
- `POST /api/auth/reset-password` - Request password reset
- `POST /api/auth/new-password` - Set new password

### Spaces

- `GET /api/spaces` - List spaces with filters
- `POST /api/spaces` - Create a new space
- `GET /api/spaces/<id>` - Get space details
- `PUT /api/spaces/<id>` - Update space
- `DELETE /api/spaces/<id>` - Delete space

### Bookings

- `GET /api/bookings` - List bookings
- `POST /api/bookings` - Create a new booking
- `GET /api/bookings/<id>` - Get booking details
- `PUT /api/bookings/<id>` - Update booking
- `DELETE /api/bookings/<id>` - Cancel booking

### Admin

- `GET /api/admin/users` - List users
- `POST /api/admin/users` - Create user
- `PUT /api/admin/users/<id>` - Update user
- `DELETE /api/admin/users/<id>` - Delete user
- `GET /api/admin/spaces` - List all spaces
- `GET /api/admin/bookings` - List all bookings

## Testing

Run tests with:
```bash
pytest
```

Generate coverage report:
```bash
pytest --cov=app tests/
```

## Deployment

The application can be deployed to various platforms. Here's an example for Heroku:

1. Create a new Heroku app
2. Set up the environment variables
3. Deploy using Git:
```bash
git push heroku main
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 