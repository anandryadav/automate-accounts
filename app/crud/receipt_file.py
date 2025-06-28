from sqlalchemy.orm import Session

from app.models import ReceiptFile


def create_receipt_file(db: Session, file_name: str, file_path: str) -> ReceiptFile:
    db_file = ReceiptFile(file_name=file_name, file_path=file_path)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def get_receipt_file(db: Session, file_id: int) -> ReceiptFile | None:
    return db.query(ReceiptFile).filter(ReceiptFile.id == file_id).first()


def update_validation_status(db: Session, file_id: int, is_valid: bool, reason: str = "") -> ReceiptFile | None:
    db_file = get_receipt_file(db, file_id)
    if db_file:
        db_file.is_valid = is_valid
        db_file.invalid_reason = reason
        db.commit()
        db.refresh(db_file)
    return db_file


def mark_as_processed(db: Session, file_id: int) -> ReceiptFile | None:
    db_file = get_receipt_file(db, file_id)
    if db_file:
        db_file.is_processed = True
        db.commit()
        db.refresh(db_file)
    return db_file
