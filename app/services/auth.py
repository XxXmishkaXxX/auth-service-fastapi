from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status

from schemas import auth as auth_schemas
from models.user import User
from repositories.user import UserRepository
from repositories.blacklist import BlacklistRepository
from core.config import pwd_context


class AuthService:

    def __init__(self, 
                 user_repo: UserRepository,
                 blacklist_repo: BlacklistRepository
                 ) -> None:
        self.user_repo = user_repo
        self.blacklist_repo = blacklist_repo

    async def register_user(self, data: auth_schemas.RegisterUserRequest) -> auth_schemas.RegisterUserResponse:  
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        hashed_password = pwd_context.hash(data.password)

        user = User(name=data.name,
                    email=data.email,
                    password_hash=hashed_password)

        created_user = await self.user_repo.create(user)

        return auth_schemas.RegisterUserResponse(success=True, user_id=UUID(str(created_user.id)))
    
    async def login(self, data: auth_schemas.LoginRequest) -> auth_schemas.LoginResponse:
        
        user = await self.user_repo.get_by_email(data.email)
        
        if user and pwd_context.verify(data.password, user.password_hash):
            return auth_schemas.LoginResponse(success=True, user_id=UUID(str(user.id)))
        
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or password is incorrect")

    async def logout(
        self,
        access_token: str,
        refresh_token: str,
        access_payload: dict,
        refresh_payload: dict
    ) -> auth_schemas.LogoutResponse:
        if refresh_payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )

        refresh_exp = refresh_payload.get("exp")
        if not refresh_exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token has no expiration"
            )

        access_exp = access_payload.get("exp")
        if not access_exp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Access token has no expiration"
            )
        
        await self.blacklist_repo.add(access_token, datetime.fromtimestamp(access_exp))
        await self.blacklist_repo.add(refresh_token, datetime.fromtimestamp(refresh_exp))

        return auth_schemas.LogoutResponse(success=True)