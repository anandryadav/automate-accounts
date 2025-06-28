from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReceiptFileBase(BaseModel):
    file_name: str
    file_path: str


class ReceiptFileCreate(ReceiptFileBase):
    pass


class ReceiptFile(ReceiptFileBase):
    id: int
    is_valid: Optional[bool] = None
    invalid_reason: Optional[str] = None
    is_processed: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
