from typing import Optional
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass

class Messages(Base):
    __tablename__ = "messages"
    id = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(Integer())
    chat_id: Mapped[int] = mapped_column(Integer())
    event_id: Mapped[int] = mapped_column(Integer()) # 0 - create; 1 - edit; 2 - delete
    text: Mapped[Optional[str]] = mapped_column(String(30000))