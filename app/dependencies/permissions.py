from fastapi import Depends, HTTPException
from app.dependencies.auth import get_current_user
from app.core.permissions import (
    GET_STORY_USER,
    GET_STORY_ROLE, 
    GET_STORY_PERMISSION,
    RESTORE_FROM_HISTORY  # если есть
)

# Словарь с описаниями разрешений
PERMISSIONS_INFO = {
    GET_STORY_USER: "Просмотр истории изменений пользователей",
    GET_STORY_ROLE: "Просмотр истории изменений ролей",
    GET_STORY_PERMISSION: "Просмотр истории изменений разрешений",
    "restore-from-history": "Восстановление записи из истории"
}

def require_permission(permission: str):
    """
    Фабрика зависимостей для проверки разрешений.
    """
    def permission_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "")
        
        # Только админ имеет доступ
        if user_role != "admin":
            raise HTTPException(
                status_code=403,
                detail=f"Доступ запрещен. Требуется разрешение: {permission}. "
                       f"{PERMISSIONS_INFO.get(permission, '')}"
            )
        
        return True
    
    return permission_checker