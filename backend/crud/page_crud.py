from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.page_model import Page
from schemas.page_schema import PageCreate


async def create_page(db: AsyncSession, page: PageCreate):
    db_page = Page(
        name=page.name,
        path=page.path,
        status=page.status,
        owner_id=page.owner_id,
    )
    db.add(db_page)
    await db.commit()
    await db.refresh(db_page)
    return db_page


async def get_page(db: AsyncSession, page_id: int):
    result = await db.execute(select(Page).filter(Page.id == page_id))
    return result.scalars().first()


async def get_pages_for_user(db: AsyncSession, owner_id: int):
    result = await db.execute(select(Page).filter(Page.owner_id == owner_id))
    return result.scalars().all()


async def update_page_status(db: AsyncSession, page_id: int, status: str):
    result = await db.execute(select(Page).filter(Page.id == page_id))
    db_page = result.scalars().first()
    if db_page:
        db_page.status = status
        await db.commit()
        await db.refresh(db_page)
    return db_page


async def delete_page(db: AsyncSession, page_id: int):
    result = await db.execute(select(Page).filter(Page.id == page_id))
    db_page = result.scalars().first()
    if db_page:
        await db.delete(db_page)
        await db.commit()
    return db_page
