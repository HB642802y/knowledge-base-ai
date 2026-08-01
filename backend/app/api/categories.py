from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


@router.get("/")
def list_categories():
    return [{"id": 1, "name": "Procédures", "description": "Règles opérationnelles"}]


@router.post("/")
def create_category(payload: CategoryCreate):
    return {"message": "Category created", "category": payload.model_dump()}
