import json
import os
from typing import Any, Tuple

import pytesseract
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from dotenv import load_dotenv
from openai import OpenAI
from pdf2image import convert_from_path, exceptions

from utils.logging import log

logger = log(__name__)

# Load environment variables from a .env file (for OPENAI_API_KEY)
load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_URL")
model_id = os.getenv("MODEL_ID")
poppler = os.getenv("POPPLER_PATH")

# Check if the API key is available
if not api_key:
    logger.critical("OPENAI_API_KEY not found in .env file. Please add it.")
    raise RuntimeError("OPENAI_API_KEY not found in .env file. Please add it.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key, base_url=base_url)


# --- 1. PDF Validation ---
def validate_pdf(file_path: str) -> Tuple[bool, str]:
    """
    Validates if a file is a structurally sound PDF.

    Returns:
        A tuple (is_valid: bool, reason: str)
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


# --- 2. The Main Extraction Function ---
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
    structured_data = get_structured_data_from_gpt(raw_text)

    if not structured_data:
        logger.info("AI model failed to parse the text.")
        return None

    logger.debug(structured_data)
    return structured_data


def get_structured_data_from_gpt(text: str) -> Any | None:
    """
    Sends text to OpenAI's GPT model and asks for structured JSON output.
    """
    prompt = f"""
    You are an expert receipt processing assistant. Analyze the following raw OCR text from a receipt 
    and extract the key information.

    Please provide the output in a valid JSON format with the following structure:
    {{
      "merchant_name": "string",
      "purchased_at": "YYYY-MM-DDTHH:MM:SS",
      "total_amount": "float",
      "items": [
        {{
          "description": "string",
          "quantity": "float",
          "price": "float"
        }}
      ]
    }}

    If a value is not found, use `null`. The `purchased_at` field should be a full ISO 8601 datetime if possible,
    but `YYYY-MM-DD` is also acceptable. The `items` list should contain all purchased products.

    Here is the OCR text:
    ---
    {text}
    ---
    """

    try:
        response = client.chat.completions.create(
            model=model_id,  # A model that's good with JSON
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        response_content = response.choices[0].message.content
        return json.loads(response_content)
    except Exception as e:
        logger.error(f"Error calling OpenAI API or parsing JSON: {e}")
        return None
