#!/bin/bash

# Create main backend project directories and files from project root

# Create app package and subdirectories
mkdir -p app/routes app/utils migrations scripts tests

# Create main app files
touch app/__init__.py
touch app/config.py
touch app/errors.py
touch app/models.py

# Create route files
touch app/routes/__init__.py
touch app/routes/auth.py
touch app/routes/auth_2fa.py
touch app/routes/bookings.py
touch app/routes/debug.py
touch app/routes/main.py
touch app/routes/spaces.py
touch app/routes/testimonials.py
touch app/routes/test_sendinblue.py

# Create utils files
touch app/utils/cloudinary_utils.py
touch app/utils/sendinblue_utils.py
touch app/utils/sptp_utils.py

# Create migration files
touch migrations/env.py
touch migrations/script.py.mako
mkdir -p migrations/versions

# Create scripts
touch scripts/add_role_to_test_user.py
touch scripts/assign_role_to_user.py
touch scripts/create_test_user.py
touch scripts/test_smtp_send.py
touch scripts/run_smtp_debug_server.sh

# Create test files
touch tests/test_api.py
touch tests/test_api_no_email.py
touch tests/test_api_requests.py
touch tests/test_auth_2fa.py

# Create root files
touch .gitignore
touch Dockerfile
touch requirements.txt
touch run.py

echo "Project structure touch commands executed."
