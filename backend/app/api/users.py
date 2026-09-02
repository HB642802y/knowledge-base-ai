from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import hash_password, verify_password
from ..models.user import User as DbUser

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str = Field(min_length=4)


class ProfileUpdate(BaseModel):
    id: int
    email: str
    full_name: str = Field(min_length=1)
    current_password: str | None = None
    new_password: str | None = Field(default=None, min_length=4)


def _role_for_email(email: str) -> str:
    return "admin" if email == "admin@sdsi.com" else "collaborateur"


def _public_db_user(user: DbUser) -> dict:
    email = user.email.strip().lower()
    return {
        "id": user.id,
        "email": email,
        "full_name": user.full_name,
        "role": _role_for_email(email),
    }


def current_user(x_user_email: str | None, db: Session | None = None) -> dict:
    email = (x_user_email or "").strip().lower()
    if db is not None and email:
        db_user = db.query(DbUser).filter(DbUser.email == email).first()
        if db_user:
            return _public_db_user(db_user)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session invalide.")


def admin_user(x_user_email: str | None, db: Session | None = None) -> dict:
    user = current_user(x_user_email, db)
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces reserve a l'administrateur.")
    return user


def collaborator_user(x_user_email: str | None, db: Session | None = None) -> dict:
    user = current_user(x_user_email, db)
    if user["role"] != "collaborateur":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces reserve aux collaborateurs.")
    return user


@router.get("/")
def list_users(
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    admin_user(x_user_email, db)
    db_users = [_public_db_user(user) for user in db.query(DbUser).order_by(DbUser.id.asc()).all()]
    return db_users


@router.post("/")
def create_user(
    payload: UserCreate,
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    admin_user(x_user_email, db)
    email = payload.email.strip().lower()
    if db.query(DbUser).filter(DbUser.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cet email est deja utilise.")
    if _role_for_email(email) == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Le compte admin ne peut pas etre cree ici.")

    user = DbUser(
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _public_db_user(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    admin = admin_user(x_user_email, db)
    target = db.get(DbUser, user_id)
    if target:
        target_email = target.email.strip().lower()
        if target_email == admin["email"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vous ne pouvez pas supprimer votre propre compte.")
        if _role_for_email(target_email) == "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Un compte administrateur ne peut pas etre supprime ici.")
        db.delete(target)
        db.commit()
        return

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")


@router.put("/me")
def update_my_profile(
    payload: ProfileUpdate,
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = current_user(x_user_email, db)
    if user["id"] != payload.id or user["email"] != payload.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Modification non autorisee.")

    db_user = db.query(DbUser).filter(DbUser.email == user["email"]).first()
    if db_user:
        if payload.new_password:
            if not payload.current_password or not verify_password(payload.current_password, db_user.password_hash):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mot de passe actuel incorrect.")
            db_user.password_hash = hash_password(payload.new_password)
        db_user.full_name = payload.full_name.strip()
        db.commit()
        db.refresh(db_user)
        return _public_db_user(db_user)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")
