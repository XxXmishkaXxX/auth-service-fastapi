from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import Optional
from models.user import User


class UserRepository:
    """Репозиторий для управления пользователями в базе данных."""

    def __init__(self, db: AsyncSession) -> None:
        """Инициализирует репозиторий с сессией базы данных.
        
        Args:
            db (AsyncSession): Асинхронная сессия SQLAlchemy.
        """
        self.db = db

    async def create(self, user: User) -> User:
        """Создаёт нового пользователя в базе данных.
        
        Args:
            user (User): Объект пользователя.
        
        Returns:
            User: Созданный пользователь.
        """
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(f"User with email {user.email} already exists.")
        
    async def update_user(self, user):
        """Обновляет данные пользователя в базе данных."""
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Получает пользователя по его ID.
        
        Args:
            user_id (UUID): Идентификатор пользователя.
        
        Returns:
            Optional[User]: Найденный пользователь или None, если не найден.
        """
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получает пользователя по email.
        
        Args:
            email (str): Email пользователя.
        
        Returns:
            Optional[User]: Найденный пользователь или None, если не найден.
        """
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()
    
    async def delete_user(self, user_id: UUID) -> Optional[User]:
        """Удаляет пользователя из базы данных.
        
        Args:
            user_id (UUID): Идентификатор пользователя.
        
        Returns:
            Optional[User]: Удалённый пользователь или None, если пользователь не найден.
        """
        result = await self.db.execute(select(User).filter(User.id == user_id))
        db_user = result.scalars().first()
        if db_user:
            await self.db.delete(db_user)
            await self.db.commit()
        return db_user