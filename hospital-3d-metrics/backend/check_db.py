from sqlalchemy import inspect
from app.database import engine
from app.models.user import User

def check_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Available tables:", tables)
    
    if 'users' in tables:
        print("\nColumns in users table:")
        for column in inspector.get_columns('users'):
            print(f"- {column['name']}: {column['type']}")

if __name__ == "__main__":
    check_tables()
