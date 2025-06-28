# ReceiptIQ: Automated Receipt Processing API

ReceiptIQ is a modern, high-performance API for extracting structured data from scanned PDF receipts. It uses **OCR (Tesseract)** to extract raw text and **OpenAI's GPT** to parse and format this data into a structured format, all powered by **FastAPI** and persisted using **SQLAlchemy + SQLite**.

---

## Features

- Upload scanned PDF receipts
- Validate if file is a proper PDF
- Extract structured receipt data using OpenAI GPT
- Store and retrieve receipt + line item data
- Query receipts and details via REST API
- Built-in Swagger (OpenAPI) docs

---

## Technology Stack

| Layer         | Tech                    |
|---------------|-------------------------|
| Backend       | FastAPI (Python 3.9+)   |
| OCR Engine    | Tesseract               |
| AI Parsing    | OpenAI GPT-3.5 Turbo    |
| PDF Handling  | PyPDF2, pdf2image       |
| ORM / DB      | SQLAlchemy + SQLite     |
| Server        | Uvicorn (ASGI)          |
| Containerized | Docker + Docker Compose |

---

## Prerequisites

Make sure these are installed before running the app:

- Python 3.9+
- **Tesseract OCR** — [Install Guide](https://tesseract-ocr.github.io/tessdoc/Installation.html)
- **Poppler** — required by `pdf2image`
    - macOS: `brew install poppler`
    - Debian/Ubuntu: `sudo apt-get install poppler-utils`

---

## Installation & Setup

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd automate-accounts

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the root directory with the following content:

```plaintext
OPENAI_API_KEY="sk-..."
OPENAI_URL="https://api.openai.com/v1"
MODEL_ID="gpt-3.5-turbo"
POPPLER_PATH="/path/to/poppler/bin"  # Optional on Linux/macOS
 ```

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

- App will be live at: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs

### Project Structure

```plaintext
automate-accounts/
app/
├── main.py             # FastAPI app entrypoint
├── api/                # API route definitions
├── crud/               # DB logic (CRUD)
├── schemas/            # Pydantic models
├── models/             # SQLAlchemy models
├── services/           # Business logic (OCR, LLM)
├── core/               # Dependencies (DB, DI, etc)
├── utils/              # Logging and file utilities
uploads/                # Stores uploaded PDF files
```

### API Endpoints

```plaintext
POST /receipts/upload          # Upload a PDF receipt
POST /receipts/parse           # Parse uploaded receipt
GET /receipts/{receipt_id}     # Get receipt details
GET /receipts/{receipt_id}/items # Get line items for a receipt
```

### Example Usage (via curl)

```bash
# Upload a receipt
curl -X POST -F "file=@/path/to/receipt.pdf" http://127.0.0.1:8000/upload

# Validate the uploaded receipt
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": 1}' \
  http://127.0.0.1:8000/validate

# Process the receipt using OCR + AI
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id": 1}' \
  http://127.0.0.1:8000/process
```

### Testing
To run tests, make sure you have `pytest` installed:

```bash 
pip install pytest
```

Then run:

```bash
pytest tests/
```
### Docker Support
To run the application using Docker, you can use the provided `Dockerfile` and `docker-compose.yml`.
### 1. Build the Docker image

```bash
docker build -t receipt-iq .
    or
docker-compose build
```
### 2. Run the Docker container

```bash
  
docker-compose up -d
```

### Uploads Directory
Make sure the `uploads/` directory exists and is writable by the application. You can create it manually:

```bash
mkdir uploads
chmod 777 uploads  # Make it writable for all users
```

### License
This project is open-source under the MIT License.
### Contributing
### Issues
If you find any bugs or have feature requests, please open an issue on our [GitHub Issues page](https://github.com/anandryadav/receipt-iq/issues)
### Contact
For any questions or support, please contact us at [anandryadav@aol.com](mailto:anandryadav@aol.com)