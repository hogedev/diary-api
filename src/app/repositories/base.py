from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import Base


class BaseRepository[ModelT: Base]:
    def __init__(self, session: AsyncSession, model_class: type[ModelT]):
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, id: int) -> ModelT | None:
        return cast(ModelT | None, await self.session.get(self.model_class, id))

    async def get_paginated(self, *, offset: int = 0, limit: int = 20) -> tuple[list[ModelT], int]:
        count_result = await self.session.execute(
            select(func.count()).select_from(self.model_class)
        )
        total = count_result.scalar_one()
        result = await self.session.execute(select(self.model_class).offset(offset).limit(limit))
        items = list(result.scalars().all())
        return items, total

    async def create(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelT) -> ModelT:
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
