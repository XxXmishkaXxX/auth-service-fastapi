from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from uuid import UUID
from fastapi import HTTPException, status
from app.core.config import settings


class JWTService:
    def __init__(self, secret_key: str = settings.SECRET_KEY, algorithm: str = settings.ALGORITHM):
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def create_tokens(self, user_id: UUID) -> dict:
        access_token = self._create_token({"sub": str(user_id), "type": "access"}, expires_minutes=15)
        refresh_token = self._create_token({"sub": str(user_id), "type": "refresh"}, expires_days=30)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    async def create_access_token(self, user_id: UUID) -> str:
        return self._create_token(
            data={"sub": str(user_id), "type": "access"},
            expires_minutes=15
        )

    def _create_token(self, data: dict, expires_minutes: int = None, expires_days: int = None) -> str:
        to_encode = data.copy()

        if expires_minutes:
            expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
        elif expires_days:
            expire = datetime.utcnow() + timedelta(days=expires_days)
        else:
            raise ValueError("Either expires_minutes or expires_days must be specified")

        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )



jwt_service = JWTService()