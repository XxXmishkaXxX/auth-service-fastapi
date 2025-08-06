from typing_extensions import Self
from uuid import UUID
from typing import Annotated
from pydantic import BaseModel, Field, EmailStr, model_validator

StringField = Annotated[str, Field()]


class RegisterUserRequest(BaseModel):
    """Схема пользователя на регистрацию"""
    name: StringField
    email: EmailStr
    password: StringField
    confirm_password: StringField

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self



class RegisterUserResponse(BaseModel):
    """Схема пользователя на регистрацию"""
    success : bool
    user_id: UUID


class LoginRequest(BaseModel):
    email: EmailStr
    password: StringField

class LoginResponse(BaseModel):
    success: bool
    user_id: UUID

class LogoutRequest(BaseModel):
    access_token: str
    refresh_token: str

class LogoutResponse(BaseModel):
    success: bool