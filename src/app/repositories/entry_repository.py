import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.entry import Entry
from ..models.user import User
from .base import BaseRepository


class EntryRepository(BaseRepository[Entry]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Entry)

    async def get_by_id_for_user(self, id: int, user_id: int) -> Entry | None:
        result = await self.session.execute(
            select(Entry).where(Entry.id == id, Entry.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_paginated_by_date(
        self,
        user_id: int,
        *,
        offset: int = 0,
        limit: int = 20,
        date_from: dt.date | None = None,
        date_to: dt.date | None = None,
    ) -> tuple[list[Entry], int]:
        base = select(Entry).where(Entry.user_id == user_id)
        count_base = select(func.count()).select_from(Entry).where(Entry.user_id == user_id)

        if date_from:
            base = base.where(Entry.entry_date >= date_from)
            count_base = count_base.where(Entry.entry_date >= date_from)
        if date_to:
            base = base.where(Entry.entry_date <= date_to)
            count_base = count_base.where(Entry.entry_date <= date_to)

        count_result = await self.session.execute(count_base)
        total = count_result.scalar_one()

        query = base.order_by(Entry.entry_date.desc(), Entry.created_at.desc())
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total

    async def get_dates(
        self, user_id: int, *, year: int | None = None, month: int | None = None
    ) -> list[dt.date]:
        query = (
            select(Entry.entry_date)
            .where(Entry.user_id == user_id)
            .distinct()
            .order_by(Entry.entry_date.desc())
        )
        if year:
            query = query.where(func.strftime("%Y", Entry.entry_date) == str(year))
        if year and month:
            query = query.where(func.strftime("%m", Entry.entry_date) == f"{month:02d}")
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # --- 公開API用 ---

    async def get_public_by_id(self, id: int) -> Entry | None:
        result = await self.session.execute(
            select(Entry)
            .join(User, Entry.user_id == User.id)
            .where(Entry.id == id, Entry.is_public.is_(True), User.is_public.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_public_paginated(
        self,
        *,
        username: str | None = None,
        offset: int = 0,
        limit: int = 20,
        date_from: dt.date | None = None,
        date_to: dt.date | None = None,
    ) -> tuple[list[Entry], int]:
        base = (
            select(Entry)
            .join(User, Entry.user_id == User.id)
            .where(Entry.is_public.is_(True), User.is_public.is_(True))
        )
        count_base = (
            select(func.count())
            .select_from(Entry)
            .join(User, Entry.user_id == User.id)
            .where(Entry.is_public.is_(True), User.is_public.is_(True))
        )

        if username:
            base = base.where(User.username == username)
            count_base = count_base.where(User.username == username)
        if date_from:
            base = base.where(Entry.entry_date >= date_from)
            count_base = count_base.where(Entry.entry_date >= date_from)
        if date_to:
            base = base.where(Entry.entry_date <= date_to)
            count_base = count_base.where(Entry.entry_date <= date_to)

        count_result = await self.session.execute(count_base)
        total = count_result.scalar_one()

        query = base.order_by(Entry.entry_date.desc(), Entry.created_at.desc())
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total

    async def get_public_dates(
        self,
        *,
        username: str | None = None,
        year: int | None = None,
        month: int | None = None,
    ) -> list[dt.date]:
        query = (
            select(Entry.entry_date)
            .join(User, Entry.user_id == User.id)
            .where(Entry.is_public.is_(True), User.is_public.is_(True))
            .distinct()
            .order_by(Entry.entry_date.desc())
        )
        if username:
            query = query.where(User.username == username)
        if year:
            query = query.where(func.strftime("%Y", Entry.entry_date) == str(year))
        if year and month:
            query = query.where(func.strftime("%m", Entry.entry_date) == f"{month:02d}")
        result = await self.session.execute(query)
        return list(result.scalars().all())
