from typing import Optional, List
from pydantic import BaseModel, HttpUrl, constr
from datetime import datetime

class AuthorizationRequest(BaseModel):
    response_type: str
    client_id: str
    redirect_uri: HttpUrl
    scope: str
    state: str
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = "S256"

class AuthorizationResponse(BaseModel):
    code: str
    state: str

class ConsentRequest(BaseModel):
    client_id: str
    scopes: List[str]
    redirect_uri: HttpUrl
    state: str

class ConsentResponse(BaseModel):
    granted: bool
    scopes: List[str]

class ClientInfo(BaseModel):
    name: str
    description: Optional[str]
    website: Optional[HttpUrl]
    terms_url: Optional[HttpUrl]
    privacy_url: Optional[HttpUrl]
    logo_url: Optional[HttpUrl]

class ScopeInfo(BaseModel):
    name: str
    description: str
    required: bool = False

class AuthorizationPageData(BaseModel):
    client: ClientInfo
    requested_scopes: List[ScopeInfo]
    user_email: str
    consent_url: HttpUrl
    cancel_url: HttpUrl
