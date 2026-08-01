from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def admin_stats():
    return {"documents": 1, "users": 1, "conversations": 0}
