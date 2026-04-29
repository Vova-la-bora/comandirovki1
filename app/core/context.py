# app/core/context.py
from contextvars import ContextVar
from typing import Optional

_current_user_id: ContextVar[Optional[int]] = ContextVar('current_user_id', default=None)

def set_current_user_id(user_id: int) -> None:
    _current_user_id.set(user_id)

def get_current_user_id() -> Optional[int]:
    """Возвращает ID текущего пользователя или None"""
    return _current_user_id.get()