from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class OAuth2Token(Base):
    __tablename__ = 'oauth2_tokens'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('oauth2_clients.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Token data
    token_type = Column(String(40))
    access_token = Column(String(255), unique=True)
    refresh_token = Column(String(255), unique=True)
    scope = Column(String(1000))  # space-separated list of scopes
    
    # Revocation and expiry
    revoked = Column(Boolean, default=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    client = relationship('OAuth2Client', back_populates='tokens')
    user = relationship('User', back_populates='oauth2_tokens')
    
    def __repr__(self):
        return f"<OAuth2Token {self.id} for user {self.user_id}>"
