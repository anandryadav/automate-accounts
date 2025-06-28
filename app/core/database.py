from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ----------------------------------------
# Database Configuration
# ----------------------------------------

# Database URL format:
# For SQLite: "sqlite:///./filename.db"
# For PostgreSQL: "postgresql://user:password@host:port/dbname"
DATABASE_URL = "sqlite:///./receipts.db"

# ----------------------------------------
# Create SQLAlchemy Engine
# ----------------------------------------

# For SQLite only: 'check_same_thread' must be False to allow
# usage across multiple threads in FastAPI (like in async endpoints).
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# ----------------------------------------
# Create a Session Factory
# ----------------------------------------

# `SessionLocal` is a class you can instantiate to create a new DB session.
# It handles transaction scope and integrates cleanly with FastAPI's dependency system.
SessionLocal = sessionmaker(
    autocommit=False,  # Control when commit happens
    autoflush=False,  # Avoid auto-flushing pending changes to DB
    bind=engine  # Attach engine to session
)

# ----------------------------------------
# Base ORM Class
# ----------------------------------------

# All your models will inherit from this Base class.
# SQLAlchemy uses it to track table definitions and relationships.
Base = declarative_base()
