import os
from typing import Any, Tuple

import pytesseract
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from dotenv import load_dotenv
from pdf2image import convert_from_path, exceptions

from app.services.llm_service import LLMService
from utils.logging import log

logger = log(__name__)

llm = LLMService()
# Load environment variables from a .env file (for OPENAI_API_KEY)
load_dotenv()

# Fetch the API key from environment variables
poppler = os.getenv("POPPLER_PATH")


# --- 1. PDF Validation ---
def validate_pdf(file_path: str) -> Tuple[bool, str]:
    """
    Validates whether the file at the given path is a readable and intact PDF.
    Args:
        file_path (str): Absolute path to the PDF file.
    Returns:
        Tuple[bool, str]: A tuple with validation status and message.
    """
    try:
        with open(file_path, 'rb') as f:
            PdfReader(f)
        logger.info(f"File {file_path} is a valid PDF.")
        return True, "File is a valid PDF."
    except PdfReadError:
        return False, "File is not a valid PDF or is corrupted."
    except FileNotFoundError:
        return False, "File not found at the specified path."
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"


# --- 2. Main OCR + AI Extraction Pipeline ---
def extract_data_from_receipt(file_path: str) -> dict[str, Any] | None:
    """
    Orchestrates the entire process of extracting structured data from a PDF receipt.
    1. Convert PDF to images.
    2. Run OCR on images to get raw text.
    3. Sends raw text to an AI model for structured data extraction.

    Returns:
        A dictionary containing the extracted receipt data.
    """
    logger.info(f"Starting extraction for: {file_path}")

    POPPLER_PATH = poppler

    # Step 1: Convert PDF to a list of PIL Images
    try:
        images = convert_from_path(pdf_path=file_path, poppler_path=POPPLER_PATH)

    except exceptions.PDFInfoNotInstalledError:
        logger.critical(f"Poppler not found at path: {POPPLER_PATH}")
        logger.critical("Please verify the poppler_path variable in ocr_service.py is correct.")
        return None
    except Exception as e:
        logger.error(f"An error occurred during PDF to Image conversion: {e}")
        return None

    # Step 2: Run OCR on each image and concatenate the text
    raw_text = ""
    for img in images:
        try:
            raw_text += pytesseract.image_to_string(img) + "\n\n"
        except pytesseract.TesseractNotFoundError:
            raise Exception("Tesseract is not installed or not in your PATH.")
        except Exception as e:
            logger.error(f"Error during OCR on an image page: {e}")
            continue

    if not raw_text.strip():
        logger.info("OCR process yielded no text.")
        return None

    logger.debug("--- Raw OCR Text ---")
    logger.debug(raw_text[:1000])
    logger.debug("--------------------")

    # Step 3: Use AI (GPT) to parse the raw text into structured JSON
    structured_data = llm.parse_receipt_text(raw_text=raw_text)

    if not structured_data:
        logger.info("AI model failed to parse the text.")
        return None

    logger.debug(structured_data)
    return structured_data
