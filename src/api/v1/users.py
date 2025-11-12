from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def get_users():
    return {"message": "Get users endpoint"}

@router.post("/users")
def create_user():
    return {"message": "Create user endpoint"}