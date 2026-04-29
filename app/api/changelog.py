from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.change_log import ChangeLog
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.dto.changelog_dto import ChangeLogDTO
from app.dto.changelog_collection_dto import ChangeLogCollectionDTO
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_permission
from app.utils.changes import calculate_changes
from app.core.context import get_current_user_id

from app.core.permissions import (
    GET_STORY_USER,
    GET_STORY_ROLE,
    GET_STORY_PERMISSION,
)

router = APIRouter(tags=["Audit"])


def _get_entity_story(
    db: Session,
    entity_type: str,
    entity_id: int
) -> ChangeLogCollectionDTO:
    logs = (
        db.query(ChangeLog)
        .filter(
            ChangeLog.entity_type == entity_type,
            ChangeLog.entity_id == entity_id
        )
        .order_by(ChangeLog.created_at.desc())
        .all()
    )
    
    items = []
    for log in logs:
        changed_fields = calculate_changes(log.before, log.after)
        
        items.append(ChangeLogDTO(
            id=log.id,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            changed_fields=changed_fields,
            created_at=log.created_at,
            created_by=log.created_by
        ))
    
    return ChangeLogCollectionDTO(
        items=items,
        total=len(items),
        entity_type=entity_type,
        entity_id=entity_id
    )


@router.get("/api/ref/user/{user_id}/story")
def user_story(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _ = Depends(require_permission(GET_STORY_USER))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _get_entity_story(db, "user", user_id)


@router.get("/api/ref/policy/role/{role_id}/story")
def role_story(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _ = Depends(require_permission(GET_STORY_ROLE))
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return _get_entity_story(db, "role", role_id)


@router.get("/api/ref/policy/permission/{permission_id}/story")
def permission_story(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _ = Depends(require_permission(GET_STORY_PERMISSION))
):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return _get_entity_story(db, "permission", permission_id)


@router.post("/api/ref/changelog/{log_id}/restore")
def restore(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _ = Depends(require_permission("restore-from-history"))
):
    """Восстановление записи из истории"""
    from app.services.audit_service import AuditService  # ДОБАВИТЬ импорт
    
    log = db.query(ChangeLog).filter(ChangeLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Change log not found")
    
    ENTITY_MAP = {
        "user": User,
        "role": Role,
        "permission": Permission
    }
    
    model = ENTITY_MAP.get(log.entity_type)
    if not model:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {log.entity_type}")
    
    entity = db.query(model).filter(model.id == log.entity_id).first()
    
    # Сохраняем состояние ДО восстановления
    current_state = entity.to_dict() if entity else {}
    
    try:
        if entity:
            for key, value in log.before.items():
                if key != "id" and hasattr(entity, key):
                    setattr(entity, key, value)
        else:
            entity = model(**log.before)
            db.add(entity)
            db.flush()
        
        # ДОБАВИТЬ: создаём лог операции восстановления
        AuditService.create_log(
            db=db,
            entity_type=log.entity_type,
            entity_id=entity.id,
            before=current_state,
            after=entity.to_dict(),
            created_by=current_user.get("id", 1)
        )
        
        db.commit()
        
        return {
            "status": "restored",
            "message": f"Entity {log.entity_type} with id {log.entity_id} restored from log {log_id}"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")