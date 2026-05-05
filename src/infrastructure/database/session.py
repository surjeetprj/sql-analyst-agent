from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from src.infrastructure.config import get_backend_settings
settings = get_backend_settings()

# 1. The Engine: This is the actual connection pool to PostgreSQL
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=True,       # Set to False in production. True prints all SQL to the terminal!
    future=True,
    pool_size=5,     # Keep 5 connections open and ready
    max_overflow=10  # Allow up to 10 extra connections during traffic spikes
)

# 2. The Session Factory: This generates new "conversations" with the database
AsyncSessionFactory = async_sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

# 3. The Dependency Injector (Crucial for FastAPI)
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    This function gives a fresh database session to every API request.
    It automatically closes the connection when the request is done.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            # If everything worked perfectly, save the changes
            await session.commit()
        except Exception:
            # If the AI or the User caused an error, undo any database changes!
            await session.rollback()
            raise
        finally:
            # Always close the connection to prevent memory leaks
            await session.close()