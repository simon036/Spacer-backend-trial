import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

app = create_app()
app.app_context().push()

with db.engine.connect() as connection:
    connection.execute(text("UPDATE alembic_version SET version_num = 'becb2892fb45'"))
    print("Alembic version reset to 'becb2892fb45'")
