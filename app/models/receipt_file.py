from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ReceiptFile(Base):
    __tablename__ = 'receipt_file'

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False, unique=True)
    is_valid = Column(Boolean, nullable=True)
    invalid_reason = Column(String, nullable=True)
    is_processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    receipts = relationship("Receipt", back_populates="receipt_file", cascade="all, delete-orphan")
