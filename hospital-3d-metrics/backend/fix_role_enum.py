from sqlalchemy import create_engine, text
from app.database import DatabaseConfig
import os

def fix_role_enum():
    # Get database configuration
    config = DatabaseConfig()
    engine = create_engine(config.get_connection_string())
    
    with engine.connect() as conn:
        # Drop existing enum if it exists
        conn.execute(text("""
            DROP TYPE IF EXISTS userrole CASCADE;
        """))
        conn.commit()
        
        # Create the enum with uppercase values
        conn.execute(text("""
            CREATE TYPE userrole AS ENUM ('ADMIN', 'STAFF', 'USER');
        """))
        conn.commit()
        
        # Drop the old role column
        conn.execute(text("""
            ALTER TABLE users DROP COLUMN IF EXISTS role;
        """))
        conn.commit()
        
        # Add new role column with enum type
        conn.execute(text("""
            ALTER TABLE users ADD COLUMN role userrole NOT NULL DEFAULT 'USER';
        """))
        conn.commit()
        
        print("Successfully updated role column to use enum type")

if __name__ == "__main__":
    fix_role_enum()
