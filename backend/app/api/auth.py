from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import verify_password
from ..models.user import User as DbUser
from .users import _public_db_user

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    db_user = db.query(DbUser).filter(DbUser.email == email).first()
    if db_user and verify_password(payload.password, db_user.password_hash):
        return _public_db_user(db_user)

    raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")
