from fastapi import APIRouter
from app.api.v1.users import router as users_router
from app.api.v1.auth import router as auth_router
from app.api.v1.hotels import router as hotels_router
from app.api.v1.rooms import router as rooms_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["Auth"], prefix="/auth")
api_router.include_router(users_router, tags=["Users"], prefix="/users")
api_router.include_router(hotels_router, tags=["Hotels"], prefix="/hotels")
api_router.include_router(rooms_router, tags=["Rooms"], prefix=("/rooms"))