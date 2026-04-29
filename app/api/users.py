from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from typing import Optional  # ← ДОБАВИТЬ

from sqlalchemy.orm import Session

from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User

from app.dependencies.auth import get_current_user
from app.core.security import hash_password


router = APIRouter(tags=["Users"])


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserUpdate(BaseModel):  # ← ДОБАВИТЬ
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


@router.post("/users")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.get("role") != "admin":
        raise HTTPException(403, "Only admin can create users")
    
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")
    
    new_user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user.to_dict()


@router.put("/users/{user_id}")  # ← ДОБАВИТЬ ЭТОТ ЭНДПОИНТ
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Проверка прав (админ или сам пользователь)
    if user.get("role") != "admin" and user.get("id") != user_id:
        raise HTTPException(403, "Access denied")
    
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    
    # Обновляем только переданные поля
    if data.name is not None:
        u.name = data.name
    if data.email is not None:
        existing = db.query(User).filter(
            User.email == data.email, 
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(400, "Email already exists")
        u.email = data.email
    if data.password is not None:
        u.password = hash_password(data.password)
    
    db.commit()
    db.refresh(u)
    
    return u.to_dict()


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    hard: bool = False
):
    if user.get("role") != "admin":
        raise HTTPException(403, "Only admin can delete users")
    
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    
    if hard:
        db.delete(u)
    else:
        u.soft_delete()
    db.commit()
    
    return {
        "status": "deleted",
        "user_id": user_id,
        "hard": hard,
        "deleted_at": u.deleted_at.isoformat() if u.deleted_at else None
    }


@router.post("/users/{user_id}/restore")
def restore_user(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.get("role") != "admin":
        raise HTTPException(403, "Only admin can restore users")
    
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    
    if u.deleted_at is None:
        raise HTTPException(400, "User is not deleted")
    
    u.restore()
    db.commit()
    
    return {"status": "restored", "user_id": user_id}