from uuid import UUID
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Response,
    Cookie,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer

from schemas import auth as auth_schemas
from schemas import jwt_tokens as jwt_schemas
from services.auth import AuthService
from services.jwt_tokens import jwt_service
from dependencies import get_auth_service

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@router.post("/register")
async def register(
    data: auth_schemas.RegisterUserRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Register a new user."""
    return await service.register_user(data)


@router.post("/login", response_model=jwt_schemas.TokenResponse)
async def login(
    data: auth_schemas.LoginRequest,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> jwt_schemas.TokenResponse:
    """Authenticate user and return tokens."""
    resp_data = await service.login(data)
    if resp_data.success:
        tokens = await jwt_service.create_tokens(resp_data.user_id)
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=30 * 24 * 3600,
        )
        return jwt_schemas.TokenResponse(
            access_token=tokens["access_token"],
            token_type="bearer",
        )

@router.post("/logout")
async def logout(
    response: Response,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    refresh_token: Annotated[str | None, Cookie()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> auth_schemas.LogoutResponse:
    """Invalidate tokens and clear refresh token."""
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token missing",
        )
    
    access_payload = await jwt_service.decode_token(access_token)
    refresh_payload = await jwt_service.decode_token(refresh_token)
    
    await auth_service.logout(access_token, refresh_token, access_payload, refresh_payload)
    
    response.delete_cookie(key="refresh_token")
    return auth_schemas.LogoutResponse(success=True)


@router.post("/refresh", response_model=jwt_schemas.TokenResponse)
async def refresh_token(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> jwt_schemas.TokenResponse:
    """Generate new access token using refresh token."""
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
    
    await auth_service.is_token_blacklisted(refresh_token)

    payload = await jwt_service.decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_id = UUID(payload["sub"])
    access_token = await jwt_service.create_access_token(user_id)
    return jwt_schemas.TokenResponse(access_token=access_token)