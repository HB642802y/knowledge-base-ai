from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..core.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str


fake_users = {
    "admin@sdsi.com": {"id": 1, "email": "admin@sdsi.com", "full_name": "Admin SDSI", "password": hash_password("admin123")},
}


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest):
    user = fake_users.get(payload.email)
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"id": user["id"], "email": user["email"], "full_name": user["full_name"]}
