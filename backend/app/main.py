from fastapi import FastAPI
from app.api.api import api_router

def create_app():
    app = FastAPI(title="Hotel Booking System")
    app.include_router(api_router, prefix="/api/v1")
    return app

app = create_app()
