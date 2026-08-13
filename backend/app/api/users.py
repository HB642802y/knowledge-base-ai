from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.services.user_service import get_user_by_email, get_user_by_id

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2)
    password: str = Field(min_length=4)
    role: str = "collaborateur"


class UserAdminOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    password_plain: str | None = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    current_password: str | None = None
    new_password: str | None = None


@router.get("/", response_model=list[UserAdminOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()


@router.post("/", response_model=UserAdminOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    email = str(payload.email).lower().strip()
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Cet email existe déjà")

    role = payload.role if payload.role in ("admin", "collaborateur") else "collaborateur"
    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        password_plain=payload.password,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if user.role == "admin" and db.query(User).filter(User.role == "admin").count() <= 1:
        raise HTTPException(status_code=400, detail="Impossible de supprimer le dernier admin")
    db.delete(user)
    db.commit()


@router.put("/me", response_model=UserAdminOut)
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db)):
    user = get_user_by_id(db, payload.id)
    if not user or user.email.lower() != str(payload.email).lower():
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if payload.full_name:
        user.full_name = payload.full_name.strip()

    if payload.new_password:
        if not payload.current_password or not verify_password(
            payload.current_password, user.password_hash
        ):
            raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
        user.password_hash = hash_password(payload.new_password)
        user.password_plain = payload.new_password

    db.commit()
    db.refresh(user)
    return user
