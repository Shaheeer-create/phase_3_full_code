"""
Database connection and session management.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from config import settings
import ssl


# Import all models to ensure they're registered with SQLModel
from models import Task, Conversation, Message, UserUsage
from auth_models import User


# Convert postgresql:// to postgresql+asyncpg:// for async support
# Remove sslmode parameter as asyncpg uses different SSL configuration
DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
DATABASE_URL = DATABASE_URL.split("?")[0]  # Remove query parameters

# Create SSL context for Neon
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Create async engine with SSL
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    future=True,
    connect_args={
        "ssl": ssl_context,
        "server_settings": {"jit": "off"}  # Disable JIT for better compatibility
    }
)

# Create async session maker
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    """
    Dependency for getting database sessions.

    Usage:
        @app.get("/endpoint")
        async def endpoint(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session_maker() as session:
        yield session


async def init_db():
    """
    Initialize database tables.
    Called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
