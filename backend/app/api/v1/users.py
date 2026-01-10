from fastapi import APIRouter, Depends, HTTPException
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.models.users import User
from app.api.deps import get_current_user

import logging

router = APIRouter()
logger = logging.getLogger("UsersRouter")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# db: Session = Depends(get_db) nghĩa là:
# FastAPI tạo DB session giúp bạn đưa session đó vào biến db và tự đóng nó sau khi request xong.
@router.get("/sample")
def get_sample_user(db: Session = Depends(get_db)):
    try:
        user = db.query(User).where(
            User.password_hash == '0942809417'
        ).first()

        if not user:
            logger.info("User not found")
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "created_at": user.created_at
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Unexpected error in get_sample_user")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role.value
    }
