from typing import Annotated
from fastapi import APIRouter, Depends


from schemas import auth as auth_schemas
from services.auth import AuthService
from schemas.jwt_tokens import TokenResponse
from services.jwt_tokens import jwt_service
from dependencies import get_auth_service


router = APIRouter()


@router.post("/register")
async def register(data: auth_schemas.RegisterUserRequest, 
                   service: Annotated[AuthService, Depends(get_auth_service)]):
    return await service.register_user(data)

@router.post("/login", response_model=TokenResponse)
async def login(
    data: auth_schemas.LoginRequest, 
    service: Annotated[AuthService, Depends(get_auth_service)]
) -> TokenResponse:
    resp_data = await service.login(data)
    if resp_data.success:
        jwt_data = await jwt_service.create_tokens(resp_data.user_id)
        return TokenResponse(**jwt_data)



@router.post("/logout")
async def logout(data: auth_schemas.LogoutRequest,
                 auth_service: Annotated[AuthService, Depends(get_auth_service)]
                 ) -> auth_schemas.LogoutResponse:
    
    access_payload = await jwt_service.decode_token(data.access_token)
    refresh_payload = await jwt_service.decode_token(data.refresh_token)

    return await auth_service.logout(data.access_token, data.refresh_token, access_payload, refresh_payload)
