from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from ..database import Base
from ..core.password import verify_password as verify_pwd, get_password_hash
from datetime import datetime
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"
    USER = "user"

# Association table for user roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Password reset fields
    reset_token = Column(String(255), unique=True, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # Session fields
    last_login = Column(DateTime, nullable=True)
    last_password_change = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime, nullable=True)
    locked_until = Column(DateTime, nullable=True)
    
    # Verification fields
    verification_token = Column(String(255), unique=True, nullable=True)
    verification_sent_at = Column(DateTime, nullable=True)
    
    # OAuth fields
    oauth_provider = Column(String(50), nullable=True)
    oauth_id = Column(String(255), nullable=True)
    
    # OAuth2 relationships
    oauth2_clients = relationship('OAuth2Client', back_populates='user')
    oauth2_tokens = relationship('OAuth2Token', back_populates='user')
    oauth2_consents = relationship('OAuth2Consent', back_populates='user')
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    blacklisted_tokens = relationship("BlacklistedToken", back_populates="user", cascade="all, delete-orphan")
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the hashed password."""
        return verify_pwd(password, self.hashed_password)
    
    def set_password(self, password: str) -> None:
        """Set a new password."""
        self.hashed_password = get_password_hash(password)
    
    def __repr__(self):
        return f"<User {self.username}>"

class RoleAccess(Base):
    """Role access levels for different data types."""
    __tablename__ = "role_access"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_name = Column(String, unique=True, nullable=False)
    patient_access = Column(String, nullable=False, default="none")  # none, view, limited, full
    staff_access = Column(String, nullable=False, default="none")    # none, view, limited, full
    resource_access = Column(String, nullable=False, default="none") # none, view, limited, full
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RoleAccess {self.role_name}>"
