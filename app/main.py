from fastapi import FastAPI

from app.core.database import engine
from app.models import Base
from utils.logging import log

logger = log(__name__)
# Create the FastAPI app instance
app = FastAPI(
    title="ReceiptIQ API",
    description="API for processing scanned receipts.",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    """
    Startup logic to initialize database tables.
    Ensures all models are imported and tables created if missing.
    """
    logger.info("Starting up: Creating tables if not exist...")
    Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Receipt API. Go to /docs for API documentation."}
