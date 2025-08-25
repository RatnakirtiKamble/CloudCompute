from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user_model import User
from schemas.user_schema import UserCreate
from utils.security_utils import get_password_hash


async def create_user(db: AsyncSession, user: UserCreate):
    hashed_pw = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        role=user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str):
    print(f"get_user_by_email called with email: {email}")
    result = await db.execute(select(User).filter(User.email == email))
    print(f"SQLAlchemy result: {result}")
    user = result.scalars().first()
    print(f"Found user: {user}")
    return user


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def update_user_role(db: AsyncSession, user_id: int, new_role: str):
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()
    if db_user:
        db_user.role = new_role
        await db.commit()
        await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()
    if db_user:
        await db.delete(db_user)
        await db.commit()
    return db_user
