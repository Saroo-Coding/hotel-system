from sqlalchemy import Boolean, Column, String, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Guest(Base):
    __tablename__ = "guests"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=True)
    full_name = Column(String(255), nullable=False)
    id_type = Column(String(20), nullable=False)  # CCCD / Passport
    id_number = Column(String(50), unique=True, nullable=False)  # CCCD / Passport number
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    nationality = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    del_flag = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())