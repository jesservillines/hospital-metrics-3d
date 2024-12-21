from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_client_secret,
    generate_authorization_code,
    verify_pkce_challenge,
    Token,
)
from app.core.oauth2_config import oauth2_settings
from app.database import get_db
from app.models.oauth2 import (
    OAuth2Client,
    OAuth2Token,
    OAuth2AuthorizationCode,
    OAuth2Consent,
    User,
)
from app.core.security import limiter
from app.schemas.oauth2 import (
    AuthorizationRequest,
    AuthorizationResponse,
    ConsentRequest,
    ConsentResponse,
    ClientInfo,
    ScopeInfo,
    AuthorizationPageData,
)
from app.core.templates import templates  # We'll create this later

router = APIRouter(prefix="/api/v1/oauth", tags=["oauth2"])

@router.post("/token", response_model=Token)
@limiter.limit(oauth2_settings.RATE_LIMIT_TOKEN_ENDPOINT[0])
async def token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 token endpoint supporting various grant types."""
    
    # Validate client credentials
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == form_data.client_id
    ).first()
    if not client or not verify_client_secret(form_data.client_secret, client.client_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )

    if form_data.grant_type == "authorization_code":
        return await handle_authorization_code_grant(
            db, client, form_data.code, form_data.code_verifier
        )
    elif form_data.grant_type == "refresh_token":
        return await handle_refresh_token_grant(
            db, client, form_data.refresh_token
        )
    elif form_data.grant_type == "client_credentials":
        return await handle_client_credentials_grant(
            db, client, form_data.scope.split()
        )
    elif form_data.grant_type == "password":
        return await handle_password_grant(
            db, client, form_data.username, form_data.password, form_data.scope.split()
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported grant type: {form_data.grant_type}",
        )

async def handle_authorization_code_grant(
    db: Session,
    client: OAuth2Client,
    code: str,
    code_verifier: Optional[str] = None,
) -> Token:
    """Handle the OAuth2 authorization code grant type."""
    
    auth_code = db.query(OAuth2AuthorizationCode).filter(
        OAuth2AuthorizationCode.code == code,
        OAuth2AuthorizationCode.client_id == client.id,
    ).first()

    if not auth_code or auth_code.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired authorization code",
        )

    # Verify PKCE if enabled
    if oauth2_settings.REQUIRE_PKCE and not code_verifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PKCE code_verifier is required",
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": auth_code.user_id, "client_id": client.client_id},
        scopes=auth_code.scope.split(),
    )

    # Create refresh token if offline_access scope was granted
    refresh_token = None
    if "offline_access" in auth_code.scope:
        refresh_token, expires_at = create_refresh_token(
            data={"sub": auth_code.user_id, "client_id": client.client_id},
            scopes=auth_code.scope.split(),
        )

        # Store refresh token
        db_token = OAuth2Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            scope=auth_code.scope,
            user_id=auth_code.user_id,
            client_id=client.id,
            expires_at=expires_at,
        )
        db.add(db_token)

    # Delete used authorization code
    db.delete(auth_code)
    db.commit()

    return Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        expires_in=oauth2_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=auth_code.scope,
    )

async def handle_refresh_token_grant(
    db: Session,
    client: OAuth2Client,
    refresh_token: str,
) -> Token:
    """Handle the OAuth2 refresh token grant type."""
    
    token = db.query(OAuth2Token).filter(
        OAuth2Token.refresh_token == refresh_token,
        OAuth2Token.client_id == client.id,
        OAuth2Token.revoked == False,
    ).first()

    if not token or token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired refresh token",
        )

    # Create new access token
    access_token = create_access_token(
        data={"sub": token.user_id, "client_id": client.client_id},
        scopes=token.scope.split(),
    )

    # Optionally rotate refresh token
    new_refresh_token = None
    if oauth2_settings.ROTATE_REFRESH_TOKENS:
        new_refresh_token, expires_at = create_refresh_token(
            data={"sub": token.user_id, "client_id": client.client_id},
            scopes=token.scope.split(),
        )
        
        # Update token in database
        token.access_token = access_token
        token.refresh_token = new_refresh_token
        token.expires_at = expires_at
    else:
        token.access_token = access_token

    db.commit()

    return Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=new_refresh_token or refresh_token,
        expires_in=oauth2_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=token.scope,
    )

async def handle_client_credentials_grant(
    db: Session,
    client: OAuth2Client,
    scopes: list[str],
) -> Token:
    """Handle the OAuth2 client credentials grant type."""
    
    # Validate requested scopes against allowed client scopes
    allowed_scopes = set(client.scope.split())
    for scope in scopes:
        if scope not in allowed_scopes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested scope not allowed: {scope}",
            )

    # Create access token
    access_token = create_access_token(
        data={"sub": f"client:{client.client_id}", "client_id": client.client_id},
        scopes=scopes,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=oauth2_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=" ".join(scopes),
    )

async def handle_password_grant(
    db: Session,
    client: OAuth2Client,
    username: str,
    password: str,
    scopes: list[str],
) -> Token:
    """Handle the OAuth2 password grant type."""
    
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "client_id": client.client_id},
        scopes=scopes,
    )

    # Create refresh token if offline_access scope is requested
    refresh_token = None
    if "offline_access" in scopes:
        refresh_token, expires_at = create_refresh_token(
            data={"sub": user.username, "client_id": client.client_id},
            scopes=scopes,
        )

        # Store refresh token
        db_token = OAuth2Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            scope=" ".join(scopes),
            user_id=user.id,
            client_id=client.id,
            expires_at=expires_at,
        )
        db.add(db_token)
        db.commit()

    return Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        expires_in=oauth2_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=" ".join(scopes),
    )

@router.get("/authorize")
@limiter.limit(oauth2_settings.RATE_LIMIT_AUTH_ENDPOINT[0])
async def authorize(
    request: Request,
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = "S256",
    db: Session = Depends(get_db),
):
    """OAuth2 authorization endpoint."""
    
    # Validate request parameters
    if response_type != "code":
        return create_error_response(
            redirect_uri,
            "unsupported_response_type",
            "Only 'code' response type is supported",
            state,
        )

    # Validate client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == client_id
    ).first()
    if not client:
        return create_error_response(
            redirect_uri,
            "invalid_client",
            "Invalid client_id",
            state,
        )

    # Validate redirect URI
    if redirect_uri not in client.redirect_uris.split():
        return create_error_response(
            redirect_uri,
            "invalid_redirect_uri",
            "Redirect URI not registered for this client",
            state,
        )

    # Validate scopes
    requested_scopes = scope.split()
    allowed_scopes = set(client.scope.split())
    invalid_scopes = [s for s in requested_scopes if s not in allowed_scopes]
    if invalid_scopes:
        return create_error_response(
            redirect_uri,
            "invalid_scope",
            f"Invalid scopes requested: {', '.join(invalid_scopes)}",
            state,
        )

    # Validate PKCE if required
    if oauth2_settings.REQUIRE_PKCE and not code_challenge:
        return create_error_response(
            redirect_uri,
            "invalid_request",
            "PKCE code_challenge is required",
            state,
        )

    if code_challenge_method not in ["S256", "plain"]:
        return create_error_response(
            redirect_uri,
            "invalid_request",
            "Unsupported code_challenge_method",
            state,
        )

    # Store authorization request in session
    request.session["auth_request"] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
    }

    # Check if user is authenticated
    user = await get_current_user(request)
    if not user:
        # Redirect to login page with return_to parameter
        return RedirectResponse(
            url=f"/login?return_to={request.url}",
            status_code=status.HTTP_302_FOUND,
        )

    # Check if user has already consented to these scopes for this client
    consent = db.query(OAuth2Consent).filter(
        OAuth2Consent.user_id == user.id,
        OAuth2Consent.client_id == client.id,
    ).first()

    if consent and all(s in consent.scope.split() for s in requested_scopes):
        # User has already consented, proceed with authorization
        return await handle_authorization(
            request,
            user,
            client,
            redirect_uri,
            requested_scopes,
            state,
            code_challenge,
            code_challenge_method,
            db,
        )

    # Prepare consent page data
    scope_info = [
        ScopeInfo(
            name=scope,
            description=get_scope_description(scope),
            required=scope in oauth2_settings.DEFAULT_SCOPES,
        )
        for scope in requested_scopes
    ]

    client_info = ClientInfo(
        name=client.client_name,
        description=client.client_metadata.get("description"),
        website=client.client_metadata.get("website"),
        terms_url=client.client_metadata.get("terms_url"),
        privacy_url=client.client_metadata.get("privacy_url"),
        logo_url=client.client_metadata.get("logo_url"),
    )

    page_data = AuthorizationPageData(
        client=client_info,
        requested_scopes=scope_info,
        user_email=user.email,
        consent_url=str(request.url_for("handle_consent")),
        cancel_url=create_error_redirect_url(
            redirect_uri,
            "access_denied",
            "The user denied the authorization request",
            state,
        ),
    )

    # Show consent page
    return templates.TemplateResponse(
        "oauth2_consent.html",
        {
            "request": request,
            "page_data": page_data,
        },
    )

@router.post("/consent")
async def handle_consent(
    request: Request,
    consent_data: ConsentRequest,
    db: Session = Depends(get_db),
):
    """Handle user consent for OAuth2 authorization."""
    
    # Get user from session
    user = await get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Get client
    client = db.query(OAuth2Client).filter(
        OAuth2Client.client_id == consent_data.client_id
    ).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client_id",
        )

    # Store consent
    consent = OAuth2Consent(
        user_id=user.id,
        client_id=client.id,
        scope=" ".join(consent_data.scopes),
        expires_at=datetime.utcnow() + timedelta(days=oauth2_settings.CONSENT_EXPIRE_DAYS),
    )
    db.add(consent)
    db.commit()

    # Get authorization request from session
    auth_request = request.session.get("auth_request")
    if not auth_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No authorization request found",
        )

    # Process authorization
    return await handle_authorization(
        request,
        user,
        client,
        auth_request["redirect_uri"],
        consent_data.scopes,
        auth_request["state"],
        auth_request.get("code_challenge"),
        auth_request.get("code_challenge_method", "S256"),
        db,
    )

async def handle_authorization(
    request: Request,
    user: User,
    client: OAuth2Client,
    redirect_uri: str,
    scopes: List[str],
    state: str,
    code_challenge: Optional[str],
    code_challenge_method: str,
    db: Session,
) -> RedirectResponse:
    """Generate authorization code and redirect to client."""
    
    # Generate authorization code
    auth_code = generate_authorization_code()

    # Store authorization code
    code = OAuth2AuthorizationCode(
        code=auth_code,
        client_id=client.id,
        user_id=user.id,
        redirect_uri=redirect_uri,
        scope=" ".join(scopes),
        expires_at=datetime.utcnow() + timedelta(minutes=oauth2_settings.AUTH_CODE_EXPIRE_MINUTES),
    )

    if code_challenge:
        code.code_challenge = code_challenge
        code.code_challenge_method = code_challenge_method

    db.add(code)
    db.commit()

    # Clear authorization request from session
    request.session.pop("auth_request", None)

    # Redirect back to client
    params = {
        "code": auth_code,
        "state": state,
    }
    redirect_url = f"{redirect_uri}?{urlencode(params)}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

def create_error_response(
    redirect_uri: str,
    error: str,
    error_description: str,
    state: Optional[str] = None,
) -> RedirectResponse:
    """Create error response for OAuth2 authorization endpoint."""
    return RedirectResponse(
        url=create_error_redirect_url(redirect_uri, error, error_description, state),
        status_code=status.HTTP_302_FOUND,
    )

def create_error_redirect_url(
    redirect_uri: str,
    error: str,
    error_description: str,
    state: Optional[str] = None,
) -> str:
    """Create error redirect URL for OAuth2 authorization endpoint."""
    params = {
        "error": error,
        "error_description": error_description,
    }
    if state:
        params["state"] = state
    return f"{redirect_uri}?{urlencode(params)}"

def get_scope_description(scope: str) -> str:
    """Get human-readable description for OAuth2 scope."""
    scope_descriptions = {
        "metrics:read": "Read access to hospital metrics data",
        "metrics:write": "Write access to hospital metrics data",
        "profile:read": "Access to read your basic profile information",
        "offline_access": "Access to refresh tokens for offline access",
        "openid": "Access to OpenID Connect identity information",
        "email": "Access to your email address",
    }
    return scope_descriptions.get(scope, scope)
