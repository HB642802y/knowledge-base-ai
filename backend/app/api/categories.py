from fastapi import APIRouter, Header
from pydantic import BaseModel

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


@router.get("/")
def list_categories(x_user_email: str | None = Header(default=None)):
    admin_user(x_user_email)
    return [{"id": 1, "name": "Procédures", "description": "Règles opérationnelles"}]


@router.post("/")
def create_category(payload: CategoryCreate, x_user_email: str | None = Header(default=None)):
    admin_user(x_user_email)
    return {"message": "Category created", "category": payload.model_dump()}
from .users import admin_user
