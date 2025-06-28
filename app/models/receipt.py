from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Receipt(Base):
    __tablename__ = 'receipt'

    id = Column(Integer, primary_key=True, index=True)
    receipt_file_id = Column(Integer, ForeignKey('receipt_file.id', ondelete='CASCADE'), nullable=False)
    purchased_at = Column(DateTime, nullable=True)
    merchant_name = Column(String, nullable=True)
    total_amount = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    receipt_file = relationship("ReceiptFile", back_populates="receipts")
    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")
