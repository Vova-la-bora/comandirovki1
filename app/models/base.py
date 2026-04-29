from sqlalchemy import Column, Boolean, DateTime
from datetime import datetime

class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        self.is_deleted = False
        self.deleted_at = None