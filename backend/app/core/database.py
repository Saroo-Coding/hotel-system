from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False  # LOG SQL để debug
)

# autocommit=False — không tự động commit; phải gọi db.commit() rõ ràng khi muốn lưu thay đổi.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo một session factory để sử dụng trong các route
session = scoped_session(SessionLocal)