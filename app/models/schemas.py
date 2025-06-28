from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# Receipt File Table
class ReceiptFile(Base):
    __tablename__ = 'receipt_file'
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_path = Column(String, unique=True)
    is_valid = Column(Boolean, nullable=True)
    invalid_reason = Column(String, nullable=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Receipt Table
class Receipt(Base):
    __tablename__ = 'receipt'
    id = Column(Integer, primary_key=True, index=True)
    receipt_file_id = Column(Integer, ForeignKey('receipt_file.id'))
    purchased_at = Column(DateTime, nullable=True)
    merchant_name = Column(String, nullable=True)
    total_amount = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    receipt_file = relationship("ReceiptFile")
    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")


# Receipt Item Table
class ReceiptItem(Base):
    __tablename__ = 'receipt_item'
    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey('receipt.id'))
    description = Column(String)
    quantity = Column(Float)
    price = Column(Float)

    # Relationship
    receipt = relationship("Receipt", back_populates="items")
