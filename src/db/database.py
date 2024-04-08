from sqlmodel import create_engine, Session, SQLModel
from src.core.config import settings  # Assuming you have a settings module for configuration

DATABASE_URL = settings.DATABASE_URL  # e.g., "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)  # Set echo=False in production

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)