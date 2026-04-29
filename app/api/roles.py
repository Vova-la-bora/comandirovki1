from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from pydantic import BaseModel

from app.core.database import get_db
from app.models.role import Role
from app.dependencies.auth import get_current_user


router = APIRouter(tags=["Roles"])


class RoleCreate(BaseModel):
    name: str
    description: str


@router.post("/roles")
def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Проверка прав (только админ)
    if user.get("role") != "admin":
        raise HTTPException(403, "Only admin can create roles")
    
    # Проверка уникальности имени
    existing = db.query(Role).filter(Role.name == data.name).first()
    if existing:
        raise HTTPException(400, "Role with this name already exists")
    
    # Создаём роль (без with db.begin)
    role = Role(
        name=data.name,
        description=data.description
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    
    return role.to_dict()