from sqlalchemy import Column, String, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    CUSTOMER = "CUSTOMER"
    STAFF = "STAFF"
    ADMIN = "ADMIN"

class UserStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BANNED = "BANNED"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())