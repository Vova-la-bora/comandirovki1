# app/services/audit_service.py
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.change_log import ChangeLog


class AuditService:
    
    @staticmethod
    def create_log(
        db: Session,
        entity_type: str,
        entity_id: int,
        before: dict,
        after: dict,
        created_by: int
    ):
        """Создание лога через сессию (для операций вне observers)"""
        # Удаляем пароль из логов
        if "password" in before:
            del before["password"]
        if "password" in after:
            del after["password"]
        
        # Сериализуем datetime
        before = AuditService._serialize_dates(before)
        after = AuditService._serialize_dates(after)
        
        log = ChangeLog(
            entity_type=entity_type,
            entity_id=entity_id,
            before=before,
            after=after,
            created_by=created_by
        )
        db.add(log)
        db.flush()  # Не commit, flush только в рамках транзакции
        return log
    
    @staticmethod
    def _serialize_dates(data: dict) -> dict:
        """Рекурсивная сериализация datetime"""
        if not data:
            return data
        result = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = AuditService._serialize_dates(value)
            else:
                result[key] = value
        return result
    
    @staticmethod
    def create_log_raw(connection, entity_type, entity_id, before, after, created_by):
        """Создание лога напрямую через connection (для observers)"""
        connection.execute(
            ChangeLog.__table__.insert().values(
                entity_type=entity_type,
                entity_id=entity_id,
                before=before or {},
                after=after or {},
                created_at=datetime.utcnow(),
                created_by=created_by or 1
            )
        )