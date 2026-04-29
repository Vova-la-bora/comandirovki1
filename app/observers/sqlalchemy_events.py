# app/observers/sqlalchemy_events.py
from sqlalchemy import event
from sqlalchemy.inspection import inspect
from datetime import datetime
import json

from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.core.context import get_current_user_id


def _serialize_value(value):
    """Сериализация значений для JSON"""
    if isinstance(value, datetime):
        return value.isoformat()
    elif hasattr(value, 'to_dict'):
        return value.to_dict()
    elif isinstance(value, (list, dict)):
        return value
    return value


def _get_changes(target, connection):
    """Получение изменений в безопасной манере"""
    try:
        state = inspect(target)
        before = {}
        after = {}
        
        for attr in state.attrs:
            if attr.key == 'id':
                continue
                
            history = attr.history
            if history.has_changes():
                old_value = history.deleted[0] if history.deleted else None
                new_value = history.added[0] if history.added else getattr(target, attr.key)
                
                before[attr.key] = _serialize_value(old_value)
                after[attr.key] = _serialize_value(new_value)
        
        # Если нет изменений, ничего не возвращаем
        if not before and not after:
            return None, None
            
        return before, after
    except Exception as e:
        print(f"Error getting changes: {e}")
        return None, None


def _create_audit_log(connection, entity_type, entity_id, before, after, created_by):
    """Создание записи аудита в ТОЙ ЖЕ транзакции"""
    try:
        # Используем connection.execute для вставки в текущей транзакции
        from app.models.change_log import ChangeLog
        
        # Вставляем напрямую через SQLAlchemy core
        connection.execute(
            ChangeLog.__table__.insert().values(
                entity_type=entity_type,
                entity_id=entity_id,
                before=before or {},
                after=after or {},
                created_at=datetime.utcnow(),
                created_by=created_by or 1  # fallback для системных операций
            )
        )
        print(f"✅ Audit log created for {entity_type} ID={entity_id}")
    except Exception as e:
        print(f"❌ Failed to create audit log: {e}")
        raise  # Пробрасываем исключение для отката транзакции


def register_events(model, entity_type):
    """Регистрация событий для модели"""
    
    @event.listens_for(model, "after_insert")
    def after_insert(mapper, connection, target):
        user_id = get_current_user_id()
        # Если нет пользователя (сиды, консоль), используем ID=1 (админ)
        if not user_id:
            user_id = 1
        
        # Получаем данные после вставки
        after_data = {}
        for key, value in target.to_dict().items():
            if key != 'password' and key != 'deleted_at':
                after_data[key] = _serialize_value(value)
        
        _create_audit_log(
            connection=connection,
            entity_type=entity_type,
            entity_id=target.id,
            before={},  # При создании before пустой
            after=after_data,
            created_by=user_id
        )
    
    @event.listens_for(model, "before_update")
    def before_update(mapper, connection, target):
        # Сохраняем состояние ДО обновления в connection.info
        try:
            state = inspect(target)
            before_data = {}
            after_data = {}
            
            for attr in state.attrs:
                if attr.key == 'id' or attr.key == 'created_at':
                    continue
                
                history = attr.history
                if history.has_changes():
                    old_value = history.deleted[0] if history.deleted else None
                    new_value = history.added[0] if history.added else getattr(target, attr.key)
                    
                    # Пропускаем пароль
                    if attr.key == 'password':
                        continue
                    
                    before_data[attr.key] = _serialize_value(old_value)
                    after_data[attr.key] = _serialize_value(new_value)
            
            # Сохраняем в connection.info для after_update
            if before_data or after_data:
                key = f'_audit_{id(target)}'
                connection.info[key] = (before_data, after_data)
        except Exception as e:
            print(f"Error in before_update: {e}")
    
    @event.listens_for(model, "after_update")
    def after_update(mapper, connection, target):
        key = f'_audit_{id(target)}'
        if key in connection.info:
            before_data, after_data = connection.info.pop(key)
            
            user_id = get_current_user_id()
            if not user_id:
                user_id = 1
            
            _create_audit_log(
                connection=connection,
                entity_type=entity_type,
                entity_id=target.id,
                before=before_data,
                after=after_data,
                created_by=user_id
            )
    
    @event.listens_for(model, "before_delete")
    def before_delete(mapper, connection, target):
        # Сохраняем данные ДО удаления
        before_data = {}
        for key, value in target.to_dict().items():
            if key != 'password':
                before_data[key] = _serialize_value(value)
        
        key = f'_audit_delete_{id(target)}'
        connection.info[key] = before_data
    
    @event.listens_for(model, "after_delete")
    def after_delete(mapper, connection, target):
        key = f'_audit_delete_{id(target)}'
        if key in connection.info:
            before_data = connection.info.pop(key)
            
            user_id = get_current_user_id()
            if not user_id:
                user_id = 1
            
            _create_audit_log(
                connection=connection,
                entity_type=entity_type,
                entity_id=target.id,
                before=before_data,
                after={},  # После удаления - пусто
                created_by=user_id
            )


# Регистрируем события для всех моделей
register_events(User, "user")
register_events(Role, "role")
register_events(Permission, "permission")