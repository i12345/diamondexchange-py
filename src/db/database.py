from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings  # Assuming you have a settings module for configuration

DATABASE_URL = settings.DATABASE_URL  # e.g., "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)  # Set echo=False in production

def get_session():
    with Session(engine) as session:
        yield session

async def async_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
        
def init_db():
    SQLModel.metadata.create_all(engine)

# This ensures init_db() is only called when this script is run directly,
# not when it's imported by another module.
if __name__ == "__main__":
    init_db()