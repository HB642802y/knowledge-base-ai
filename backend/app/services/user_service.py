from sqlalchemy import Column, Integer, String, text
from sqlalchemy.orm import Session

from ..core.database import Base, engine
from ..core.security import hash_password
from ..models.user import User

DEFAULT_USERS = [
    {
        "email": "admin@sdsi.com",
        "full_name": "Admin MAPMDREF",
        "password": "admin123",
        "role": "admin",
    },
    {
        "email": "collaborateur@sdsi.com",
        "full_name": "Collaborateur MAPMDREF",
        "password": "collab123",
        "role": "collaborateur",
    },
    {
        "email": "agent@sdsi.com",
        "full_name": "Agent Rural",
        "password": "agent123",
        "role": "collaborateur",
    },
]


def migrate_users_table() -> None:
    with engine.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()}
        if "role" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'collaborateur'"))
        if "password_plain" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN password_plain VARCHAR"))
        conn.commit()


def seed_users(db: Session) -> None:
    if db.query(User).count() > 0:
        return
    for u in DEFAULT_USERS:
        db.add(
            User(
                email=u["email"],
                full_name=u["full_name"],
                password_hash=hash_password(u["password"]),
                password_plain=u["password"],
                role=u["role"],
            )
        )
    db.commit()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower().strip()).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()
