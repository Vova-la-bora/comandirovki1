from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from pydantic import BaseModel

from app.core.database import get_db
from app.models.permission import Permission
from app.dependencies.auth import get_current_user


router = APIRouter(tags=["Permissions"])


class PermissionCreate(BaseModel):
    name: str


@router.post("/permissions")
def create_permission(
    data: PermissionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Проверка прав (только админ)
    if user.get("role") != "admin":
        raise HTTPException(403, "Only admin can create permissions")
    
    # Проверка уникальности имени
    existing = db.query(Permission).filter(Permission.name == data.name).first()
    if existing:
        raise HTTPException(400, "Permission with this name already exists")
    
    # Создаём разрешение (без with db.begin)
    p = Permission(name=data.name)
    db.add(p)
    db.commit()
    db.refresh(p)
    
    return p.to_dict()