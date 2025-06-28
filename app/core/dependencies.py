from app.core.database import SessionLocal


def get_db():
    """
    FastAPI dependency to create and clean up a database session.

    This function will be called for each incoming request.
    It creates a new database session, 'yields' it to the request handler,
    and then ensures the session is closed in a 'finally' block.
    This pattern ensures the database connection is always released,
    even if an error occurs during the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
