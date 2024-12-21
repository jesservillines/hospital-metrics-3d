from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class OAuth2Consent(Base):
    __tablename__ = 'oauth2_consents'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('oauth2_clients.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    scope = Column(String(1000))  # space-separated list of scopes
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationships
    client = relationship('OAuth2Client')
    user = relationship('User', back_populates='oauth2_consents')
    
    def __repr__(self):
        return f"<OAuth2Consent {self.id} for user {self.user_id}>"
