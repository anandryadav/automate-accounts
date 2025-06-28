from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class ReceiptItem(Base):
    __tablename__ = 'receipt_item'

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey('receipt.id', ondelete='CASCADE'), nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    # Relationship
    receipt = relationship("Receipt", back_populates="items")
