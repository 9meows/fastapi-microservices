import pytest 
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.core.database import Base
from app.core.dependencies import get_async_db, get_category_validator
from app.models.post import Post


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Создаёт движок БД один раз на все тесты"""
    engine = create_async_engine(TEST_DATABASE_URL, echo = False, future = True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()
        
@pytest_asyncio.fixture(scope="session")
async def async_session_maker(test_engine):
    """Фабрика сессий для тестов"""
    return async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture()
async def app_test(async_session_maker, mock_category_validator):
    """FastAPI приложение с подменённой БД"""
    async def _get_db():
        async with async_session_maker() as session:
            try:
                yield session
            finally:
                await session.rollback()
    def _get_mock_validator():
        return mock_category_validator          
    
    app.dependency_overrides[get_async_db] = _get_db
    app.dependency_overrides[get_category_validator] = _get_mock_validator
    
    async with async_session_maker() as session:
        await session.execute(delete(Post))
        await session.commit()
    yield app
    # Очистка после тестов
    app.dependency_overrides.clear()
    
@pytest_asyncio.fixture()
async def client(app_test):
    """HTTP клиент для интеграционных тестов"""
    transport = ASGITransport(app=app_test)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c

@pytest_asyncio.fixture()
async def db_session(async_session_maker):
    """Сессия БД для unit-тестов"""
    async with async_session_maker() as session:
        await session.execute(delete(Post))
        await session.commit()
        yield session
        
@pytest.fixture()
def mock_category_validator(mocker):
    """Мок для RabitMQ валидатора категорий"""
    mock = mocker.AsyncMock()
    mock.check_exists = mocker.AsyncMock(return_value=True)
    return mock