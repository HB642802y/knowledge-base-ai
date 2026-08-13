from sqlalchemy import Column, Integer, String

from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="collaborateur", nullable=False)
    # Prototype : mot de passe visible par l'admin (à retirer en production)
    password_plain = Column(String, nullable=True)
