import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

app = create_app()
app.app_context().push()

with db.engine.connect() as connection:
    result = connection.execute(text("SELECT version_num FROM alembic_version"))
    for row in result:
        print("Current alembic version:", row[0])
