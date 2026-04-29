from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User

from app.core.security import verify_password
from app.core.security import create_access_token


router = APIRouter(tags=["Auth"])


class LoginRequest(BaseModel):

    email: str
    password: str


@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user:

        raise HTTPException(401, "Invalid credentials")

    if not verify_password(
        data.password,
        user.password
    ):

        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({
        "id": user.id,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }