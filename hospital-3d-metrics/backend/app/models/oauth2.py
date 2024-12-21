from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table, JSON, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.user import User

class OAuth2Client(Base):
    __tablename__ = 'oauth2_clients'

    id = Column(Integer, primary_key=True)
    client_id = Column(String(48), unique=True, nullable=False)
    client_secret = Column(String(120), nullable=False)
    client_name = Column(String(100))
    client_uri = Column(String(255))
    grant_types = Column(String(255))  # space-separated list of grant types
    redirect_uris = Column(String(1000))  # space-separated list of URIs
    response_types = Column(String(255))  # space-separated list of response types
    scope = Column(String(1000))  # space-separated list of scopes
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Client metadata
    client_metadata = Column(JSON)
    is_confidential = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='oauth2_clients')
    tokens = relationship('OAuth2Token', back_populates='client')

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

class OAuth2AuthorizationCode(Base):
    __tablename__ = 'oauth2_authorization_codes'

    id = Column(Integer, primary_key=True)
    code = Column(String(120), unique=True, nullable=False)
    client_id = Column(Integer, ForeignKey('oauth2_clients.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    redirect_uri = Column(String(255))
    scope = Column(String(1000))
    auth_time = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class OAuth2Consent(Base):
    __tablename__ = 'oauth2_consents'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    client_id = Column(Integer, ForeignKey('oauth2_clients.id'))
    scope = Column(String(1000))  # space-separated list of scopes
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    # Relationships
    user = relationship('User', back_populates='oauth2_consents')
