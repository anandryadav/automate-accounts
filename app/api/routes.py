import shutil
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.crud import (
    create_receipt_and_items,
    get_receipt_file,
    create_receipt_file,
    update_validation_status,
    mark_as_processed,
    get_all_receipts,
    get_receipt,
)
from app.schemas import payloads, receipt
from app.services import ocr_service
from utils.logging import log

logger = log(__name__)

# ----------------------------------------
# File Upload Configuration
# ----------------------------------------

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)  # Ensure the directory exists

router = APIRouter()


# ----------------------------------------
# Upload Receipt
# ----------------------------------------

@router.post("/upload", response_model=payloads.UploadResponse)
def upload_receipt(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """
    Uploads a receipt file (PDF only).
    Saves the file and creates a metadata record in the database.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are accepted.")

    # Create a unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOADS_DIR / unique_filename

    # Save file to disk
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Create DB record
    db_file = create_receipt_file(db, file_name=file.filename, file_path=str(file_path))
    logger.info(f"Uploaded file saved: {file.filename} -> {file_path}")
    return {"id": db_file.id, "file_name": db_file.file_name}


# ----------------------------------------
# Validate Receipt PDF
# ----------------------------------------

@router.post("/validate", response_model=payloads.ValidationResponse)
def validate_receipt(
        request: payloads.ValidationRequest,
        db: Session = Depends(get_db)
):
    """
    Validates if a receipt file is a proper PDF.
    Updates validation status in the DB.
    """
    db_file = get_receipt_file(db, file_id=request.file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    is_valid, reason = ocr_service.validate_pdf(db_file.file_path)
    update_validation_status(db, file_id=request.file_id, is_valid=is_valid, reason=reason)

    message = "File is a valid PDF." if is_valid else f"File is invalid: {reason}"
    logger.info(f"Validation result for file_id={request.file_id}: {message}")

    return {"file_id": request.file_id, "is_valid": is_valid, "message": message}


# ----------------------------------------
# Process Receipt with OCR/LLM
# ----------------------------------------

@router.post("/process", response_model=payloads.ProcessResponse)
def process_receipt(
        request: payloads.ProcessRequest,
        db: Session = Depends(get_db)
):
    """
    Processes the receipt file using OCR and AI extraction.
    Creates receipt + item records in the DB.
    """
    db_file = get_receipt_file(db, file_id=request.file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    if db_file.is_valid is not True:
        raise HTTPException(status_code=400, detail="File has not been validated or is invalid.")
    if db_file.is_processed:
        raise HTTPException(status_code=400, detail="File has already been processed.")

    try:
        # OCR + LLM extraction
        extracted_data = ocr_service.extract_data_from_receipt(db_file.file_path)
        if not extracted_data:
            raise HTTPException(status_code=500, detail="Failed to extract data from receipt.")

        # Create records
        new_receipt = create_receipt_and_items(db, extracted_data=extracted_data, file_id=db_file.id)
        mark_as_processed(db, file_id=db_file.id)

        logger.info(f"Processed receipt ID: {new_receipt.id}")
        return {"receipt_id": new_receipt.id, "message": "Receipt processed successfully."}

    except Exception as e:
        logger.exception("Exception during receipt processing")
        raise HTTPException(status_code=500, detail=f"An error occurred during processing: {str(e)}")


# ----------------------------------------
# Get All Receipts
# ----------------------------------------

@router.get("/receipts", response_model=List[receipt.Receipt])
def list_receipts(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """
    Lists all receipts with their items.
    """
    receipts = get_all_receipts(db, skip=skip, limit=limit)
    return receipts


# ----------------------------------------
# Get Specific Receipt
# ----------------------------------------

@router.get("/receipts/{receipt_id}", response_model=receipt.Receipt)
def get_receipt_details(
        receipt_id: int,
        db: Session = Depends(get_db)
):
    """
    Retrieves a single receipt by ID with full item detail.
    """
    db_receipt = get_receipt(db, receipt_id=receipt_id)
    if db_receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return db_receipt
