# Receipt: Automated Receipt Processing API

## Project Overview

Receipt is a web application with a set of REST APIs designed to automate the extraction of information from scanned PDF receipts. It uses OCR (Tesseract) to get raw text and an AI model (OpenAI GPT) to parse this text into a structured, queryable format, which is then stored in an SQLite database.

## Technology Stack

-   **Backend:** Python 3.9+
-   **Web Framework:** FastAPI
-   **Database:** SQLite
-   **ORM:** SQLAlchemy
-   **OCR Engine:** Tesseract
-   **PDF Handling:** PyPDF2, pdf2image
-   **AI Parsing:** OpenAI GPT-3.5 Turbo 
-   **Async Server:** Uvicorn

## Prerequisites

Before you begin, ensure you have the following installed on your system:
-   Python 3.9+
-   Tesseract OCR: [Installation Guide](https://tesseract-ocr.github.io/tessdoc/Installation.html)
-   Poppler: (Required by `pdf2image`)
    -   macOS: `brew install poppler`
    -   Ubuntu/Debian: `sudo apt-get install poppler-utils`

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd automate-accounts
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a file named `.env` in the root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY="sk-..."
    ```

5.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.

## API Documentation

Full interactive API documentation (provided by Swagger UI) is available at:
**http://127.0.0.1:8000/docs**

### API Endpoints

-   `POST /upload`: Upload a PDF receipt.
-   `POST /validate`: Validate if the uploaded file is a correct PDF.
-   `POST /process`: Start the OCR and AI extraction process.
-   `GET /receipts`: List all processed receipts.
-   `GET /receipts/{id}`: Get details for a specific receipt.

### Example Usage with `curl`

1.  **Upload:**
    ```bash
    curl -X POST -F "file=@/path/to/your/receipt.pdf" http://127.0.0.1:8000/upload
    ```

2.  **Validate (assuming upload returned ID 1):**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"file_id": 1}' http://127.0.0.1:8000/validate
    ```

3.  **Process:**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"file_id": 1}' http://127.0.0.1:8000/process
    ```

### Docker Support
    Step 1: Build the Docker Image
    Open your terminal in the project's root directory (/receipt-processor) and run:
    
```bash
    docker-compose build
```
    Step 2: Run the Container
    Once the build is complete, start your application with:

```bash
  docker-compose up 
```
 - To run it in the background (detached mode):

```bash
  docker-compose up -d
```

