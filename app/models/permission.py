from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.core.database import Base


class Permission(Base):

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # ДОБАВИТЬ

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None
        }
    
    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        self.deleted_at = None
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None