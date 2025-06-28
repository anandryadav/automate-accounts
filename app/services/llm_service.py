import json
import os
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

from utils.logging import log

logger = log(__name__)
load_dotenv()


class LLMService:
    """
    Handles all communication with the LLM model (e.g., OpenAI GPT) for
    parsing unstructured OCR text into structured receipt data.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_URL")
        self.model_id = model_id or os.getenv("MODEL_ID")

        if not self.api_key:
            logger.critical("OPENAI_API_KEY not provided or found in environment.")
            raise RuntimeError("Missing OPENAI_API_KEY.")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def parse_receipt_text(self, raw_text: str) -> dict[str, Any] | None:
        """
        Sends raw OCR text to the LLM and expects structured JSON receipt data.

        Args:
            raw_text (str): OCR text from receipt

        Returns:
            dict[str, Any] | None: Structured receipt fields or None on failure
        """
        prompt = self._build_prompt(raw_text)

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except Exception as e:
            logger.error(f"LLM error during JSON parsing: {e}")
            return None

    @staticmethod
    def _build_prompt(text: str) -> str:
        """
        Constructs the LLM prompt including schema instructions and OCR data.
        """
        return f"""
        You are an expert receipt processing assistant. Analyze the following raw OCR text from a receipt 
        and extract the key information.
        
        Provide the output in valid JSON with the structure:
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
        
        If a value is not found, use `null`. Use ISO 8601 format for `purchased_at`.
        
        OCR Text:
        ---
        {text}
        ---
        """
