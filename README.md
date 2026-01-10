# Hotel Booking System

# Backend

Python FastAPI backend.

Install:

pip install -r requirements.txt

Run:

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Schema (Pydantic) = lớp bảo vệ dữ liệu đầu vào, giúp API an toàn, rõ ràng và dễ scale

@router.get(...)
def handler(...):
    try:
        # 1. Validate / query
        if not condition:
            raise HTTPException(400, "Bad request")

        # 2. Business logic
        result = ...

        return result

    except HTTPException:
        raise

    except Exception:
        logger.exception("Unexpected error")
        raise HTTPException(500, "Internal Server Error")
