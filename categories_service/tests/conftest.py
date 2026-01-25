import pytest 
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.core.database import Base
from app.core.dependencies import get_async_db
from app.models.category import Category

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo = False, future = True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()
        
@pytest_asyncio.fixture(scope="session")
async def async_session_maker(test_engine):
    return async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture()
async def app_test(async_session_maker):
    async def _get_db():
        async with async_session_maker() as session:
            try:
                yield session
            finally:
                await session.rollback()
                
    app.dependency_overrides[get_async_db] = _get_db
    async with async_session_maker() as session:
        await session.execute(delete(Category))
        await session.commit()
    yield app
    # Очистка после тестов
    app.dependency_overrides.clear()
    
@pytest_asyncio.fixture()
async def client(app_test):
    transport = ASGITransport(app=app_test)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c

@pytest_asyncio.fixture()
async def db_session(async_session_maker):
    async with async_session_maker() as session:
        await session.execute(delete(Category))
        await session.commit()
        yield session