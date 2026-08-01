from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    email: str
    full_name: str


@router.get("/")
def list_users():
    return [{"id": 1, "email": "admin@sdsi.com", "full_name": "Admin SDSI"}]


@router.post("/")
def create_user(payload: UserCreate):
    return {"message": "User created", "user": payload.model_dump()}
