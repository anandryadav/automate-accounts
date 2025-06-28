from typing import Any

from dateutil import parser
from sqlalchemy.orm import Session, joinedload

from app.models import Receipt, ReceiptItem
from utils.logging import log

logger = log(__name__)


def get_receipt(db: Session, receipt_id: int) -> Receipt | None:
    return db.query(Receipt).options(joinedload(Receipt.items)).filter(Receipt.id == receipt_id).first()


def get_all_receipts(db: Session, skip: int = 0, limit: int = 100) -> list[Receipt]:
    return db.query(Receipt).options(joinedload(Receipt.items)).offset(skip).limit(limit).all()


def _safe_parse_date(date_str: str | None) -> Any:
    if not date_str:
        return None
    try:
        return parser.parse(date_str)
    except (parser.ParserError, TypeError, ValueError):
        logger.warning(f"Invalid date format: {date_str}")
        return None


def create_receipt_and_items(
        db: Session,
        extracted_data: dict[str, Any],
        file_id: int
) -> Receipt:
    parsed_date = _safe_parse_date(extracted_data.get("purchased_at"))

    db_receipt = Receipt(
        receipt_file_id=file_id,
        purchased_at=parsed_date,
        merchant_name=extracted_data.get("merchant_name"),
        total_amount=float(extracted_data.get("total_amount") or 0.0),
    )
    db.add(db_receipt)
    db.flush()  # To generate ID for FK

    for item_data in extracted_data.get("items", []):
        if not all(k in item_data for k in ["description", "quantity", "price"]):
            logger.warning(f"Incomplete item data skipped: {item_data}")
            continue

        try:
            item = ReceiptItem(
                receipt_id=db_receipt.id,
                description=item_data["description"],
                quantity=float(item_data.get("quantity") or 0.0),
                price=float(item_data.get("price") or 0.0),
            )
            db.add(item)
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid item: {item_data} | Error: {e}")
            continue

    db.commit()
    db.refresh(db_receipt)
    return db_receipt
