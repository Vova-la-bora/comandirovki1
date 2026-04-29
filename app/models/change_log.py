from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import JSON
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index

from datetime import datetime

from app.core.database import Base


class ChangeLog(Base):

    __tablename__ = "change_logs"

    id = Column(Integer, primary_key=True)

    entity_type = Column(String)

    entity_id = Column(Integer)

    before = Column(JSON)

    after = Column(JSON)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id")
    )

    __table_args__ = (
        Index("ix_entity_type", "entity_type"),
        Index("ix_entity_id", "entity_id"),
        Index("ix_created_by", "created_by"),
    )