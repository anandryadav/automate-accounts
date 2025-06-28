from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# --- Schemas for Receipt Items ---
class ReceiptItemBase(BaseModel):
    description: str
    quantity: float
    price: float


class ReceiptItemCreate(ReceiptItemBase):
    pass


class ReceiptItem(ReceiptItemBase):
    id: int
    receipt_id: int

    model_config = {
        "from_attributes": True
    }


# --- Schemas for Receipts ---
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


# --- Schemas for Receipt Files ---
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


# --- Schemas for API Payloads & Responses ---
class UploadResponse(BaseModel):
    id: int
    file_name: str


class ValidationRequest(BaseModel):
    file_id: int


class ValidationResponse(BaseModel):
    file_id: int
    is_valid: bool
    message: str


class ProcessRequest(BaseModel):
    file_id: int


class ProcessResponse(BaseModel):
    receipt_id: int
    message: str
