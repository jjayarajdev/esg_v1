import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base
from app.models.models import User, Document, QAInteraction, ESGMetric

async def init_db():
    engine = create_async_engine(
        "sqlite+aiosqlite:///./esg.db",
        echo=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db()) 