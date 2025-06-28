from typing import Dict, Any

from dateutil import parser
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models import schemas as models
from app.schemas.schemas import Receipt
from utils.logging import log

logger = log(__name__)


def create_receipt_file(db: Session, file_name: str, file_path: str) -> models.ReceiptFile:
    db_file = models.ReceiptFile(file_name=file_name, file_path=file_path)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def get_receipt_file(db: Session, file_id: int) -> models.ReceiptFile:
    return db.query(models.ReceiptFile).filter(models.ReceiptFile.id == file_id).first()


def update_validation_status(db: Session, file_id: int, is_valid: bool, reason: str = "") -> models.ReceiptFile:
    db_file = get_receipt_file(db, file_id)
    if db_file:
        db_file.is_valid = is_valid
        db_file.invalid_reason = reason
        db.commit()
        db.refresh(db_file)
    return db_file


def mark_as_processed(db: Session, file_id: int) -> models.ReceiptFile:
    db_file = get_receipt_file(db, file_id)
    if db_file:
        db_file.is_processed = True
        db.commit()
        db.refresh(db_file)
    return db_file


# --- Receipt Actions ---
def get_receipt(db: Session, receipt_id: int) -> models.Receipt:
    # Use a joined load to efficiently fetch related items in one query
    return db.query(models.Receipt).options(joinedload(models.Receipt.items)).filter(models.Receipt.id == receipt_id).first()


def get_all_receipts(db: Session, skip: int = 0, limit: int = 100) -> list[type[Receipt]]:
    return db.query(models.Receipt).options(joinedload(models.Receipt.items)).offset(skip).limit(limit).all()


def create_receipt_and_items(db: Session, extracted_data: Dict[str, Any], file_id: int) -> models.Receipt:
    # --- DATA CONVERSION AND VALIDATION STEP ---
    purchased_at_str = extracted_data.get('purchased_at')
    parsed_date = None
    if purchased_at_str:
        try:
            # Attempt to parse the date string using dateutil.parser
            parsed_date = parser.parse(purchased_at_str)
        except (parser.ParserError, TypeError):
            # Handle cases where GPT gives a weird format or not a string
            logger.error(f"Could not parse date using dateutil: {purchased_at_str}")
            parsed_date = None

    db_receipt = models.Receipt(
        receipt_file_id=file_id,
        purchased_at=parsed_date,
        merchant_name=extracted_data.get('merchant_name'),
        total_amount=float(extracted_data.get('total_amount', 0.0) or 0.0)
    )
    db.add(db_receipt)

    db.flush()

    # --- ITEM DATA PROCESSING ---
    for item_data in extracted_data.get('items', []):
        if not all(k in item_data for k in ['description', 'quantity', 'price']):
            continue

        try:
            db_item = models.ReceiptItem(
                receipt_id=db_receipt.id,
                description=item_data.get('description'),
                quantity=float(item_data.get('quantity', 0.0) or 0.0),
                price=float(item_data.get('price', 0.0) or 0.0),
            )
            db.add(db_item)
        except (ValueError, TypeError):
            logger.error(f"Could not parse item data: {item_data}")
            continue

    db.commit()
    db.refresh(db_receipt)
    return db_receipt
