from sqlalchemy.orm import Session, sessionmaker
from app.database import get_db, engine
from app.models.user import User, UserRole
from app.core.password import get_password_hash
from datetime import datetime

def create_admin_user(username: str, email: str, password: str):
    # Create database session
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.role == UserRole.ADMIN:
                print(f"Admin user {username} already exists")
                return
            else:
                # Update existing user to admin
                existing_user.role = UserRole.ADMIN
                print(f"Updated user {username} to admin role")
        else:
            # Create new admin user
            admin_user = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(password),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
                created_at=datetime.now(),
            )
            db.add(admin_user)
            print(f"Created new admin user: {username}")
        
        db.commit()
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <username> <email> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    create_admin_user(username, email, password)
