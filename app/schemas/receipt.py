from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .receipt_item import ReceiptItem


class ReceiptBase(BaseModel):
    purchased_at: Optional[datetime] = None
    merchant_name: Optional[str] = None
    total_amount: Optional[float] = None


class ReceiptCreate(ReceiptBase):
    pass


class Receipt(ReceiptBase):
    id: int
    receipt_file_id: int
    items: List[ReceiptItem] = []

    model_config = {
        "from_attributes": True
    }
