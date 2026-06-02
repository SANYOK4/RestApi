from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.users import UserModel


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> UserModel | None:
        result = await self.db.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return result.scalar_one_or_none()

    async def create(self, username: str, hashed_password: str) -> UserModel:
        user = UserModel(username=username, hashed_password=hashed_password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user