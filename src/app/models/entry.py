import datetime as dt

from sqlalchemy import Date, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Entry(TimestampMixin, Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    entry_date: Mapped[dt.date] = mapped_column(Date, nullable=False, index=True)

    photos: Mapped[list["Photo"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="entry", cascade="all, delete-orphan", lazy="selectin"
    )
