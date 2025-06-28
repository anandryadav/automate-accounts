from fastapi import FastAPI

from app.api import routes
from app.database import engine
from app.models import schemas as models

models.Base.metadata.create_all(bind=engine)

# Create the FastAPI app instance
app = FastAPI(
    title="ReceiptIQ API",
    description="API for processing scanned receipts.",
    version="1.0.0"
)

# Include the API router from api/routes.py
app.include_router(routes.router)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Receipt API. Go to /docs for API documentation."}
