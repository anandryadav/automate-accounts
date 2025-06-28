import shutil
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.crud import action as crud
from app.dependencies import get_db
from app.services import ocr_service

# Define constants
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

router = APIRouter()


@router.post("/upload", response_model=schemas.UploadResponse)
def upload_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Uploads a receipt file (PDF format only).
    Stores the file locally and creates a metadata record in the database.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are accepted.")

    # Create a unique filename to prevent collisions
    unique_id = uuid.uuid4()
    file_extension = Path(file.filename).suffix
    unique_filename = f"{unique_id}{file_extension}"
    file_path = UPLOADS_DIR / unique_filename

    # Save the file to the uploads directory
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Create the database record
    db_file = crud.create_receipt_file(db, file_name=file.filename, file_path=str(file_path))
    return {"id": db_file.id, "file_name": db_file.file_name}


@router.post("/validate", response_model=schemas.ValidationResponse)
def validate_receipt(request: schemas.ValidationRequest, db: Session = Depends(get_db)):
    """
    Validates if the uploaded file is a structurally valid PDF.
    Updates the 'is_valid' and 'invalid_reason' fields in the database.
    """
    db_file = crud.get_receipt_file(db, file_id=request.file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    is_valid, reason = ocr_service.validate_pdf(db_file.file_path)
    crud.update_validation_status(db, file_id=request.file_id, is_valid=is_valid, reason=reason)

    message = "File is a valid PDF." if is_valid else f"File is invalid: {reason}"
    return {"file_id": request.file_id, "is_valid": is_valid, "message": message}


@router.post("/process", response_model=schemas.ProcessResponse)
def process_receipt(request: schemas.ProcessRequest, db: Session = Depends(get_db)):
    """
    Extracts details from a validated receipt using OCR/AI.
    Stores the extracted information in the 'receipt' and 'receipt_item' tables.
    """
    db_file = crud.get_receipt_file(db, file_id=request.file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    if db_file.is_valid is not True:
        raise HTTPException(status_code=400, detail="File has not been validated or is invalid.")
    if db_file.is_processed:
        raise HTTPException(status_code=400, detail="File has already been processed.")

    try:
        # The heavy lifting is done in the service layer
        extracted_data = ocr_service.extract_data_from_receipt(db_file.file_path)
        if not extracted_data:
            raise HTTPException(status_code=500, detail="Failed to extract data from receipt.")

        # Create the receipt and its items in a single transaction
        new_receipt = crud.create_receipt_and_items(db, extracted_data=extracted_data, file_id=db_file.id)

        # Mark the original file as processed
        crud.mark_as_processed(db, file_id=db_file.id)

        return {"receipt_id": new_receipt.id, "message": "Receipt processed successfully."}

    except Exception as e:
        # Generic error handling for OCR/AI failures
        raise HTTPException(status_code=500, detail=f"An error occurred during processing: {str(e)}")


@router.get("/receipts", response_model=List[schemas.Receipt])
def list_receipts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lists all processed receipts stored in the database.
    Includes nested line-item details.
    """
    receipts = crud.get_all_receipts(db, skip=skip, limit=limit)
    return receipts


@router.get("/receipts/{receipt_id}", response_model=schemas.Receipt)
def get_receipt_details(receipt_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the full details of a specific receipt by its ID,
    including all associated line items.
    """
    db_receipt = crud.get_receipt(db, receipt_id=receipt_id)
    if db_receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return db_receipt
