from sqlalchemy import text
from api.database import get_db

# Get a database session
db_generator = get_db()
db = next(db_generator)

try:
    # Wrap raw SQL with text()
    result = db.execute(text("SELECT 1")).fetchone()
    print("Database connection successful! Result:", result)
except Exception as e:
    print("Database connection failed:", e)
finally:
    db.close()
