from pydantic import BaseModel


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
