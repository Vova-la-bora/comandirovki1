# from sqlalchemy import Column
# from sqlalchemy import Integer
# from sqlalchemy import String

# from app.core.database import Base


# class User(Base):

#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True)

#     name = Column(String)

#     email = Column(String)

#     password = Column(String)

#     role = Column(String, default="admin")


#     def to_dict(self):

#         return {
#             "id": self.id,
#             "name": self.name,
#             "email": self.email,
#             "role": self.role
#         }
        
        
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime  # ДОБАВИТЬ
from datetime import datetime     # ДОБАВИТЬ

from app.core.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    role = Column(String, default="admin")
    
    # ДОБАВИТЬ ЭТУ СТРОКУ
    deleted_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None  # ДОБАВИТЬ
        }
    
    # ДОБАВИТЬ ЭТИ МЕТОДЫ
    def soft_delete(self):
        """Мягкое удаление"""
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Восстановление после мягкого удаления"""
        self.deleted_at = None
    
    @property
    def is_deleted(self):
        """Проверка, удалён ли пользователь"""
        return self.deleted_at is not None