import os
import asyncio
import pytest_asyncio
from sqlmodel import SQLModel
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.database.settings import db_settings
from core.database.session import get_session
from core.main import app
from httpx import AsyncClient, ASGITransport

DATABASE_URL = db_settings.async_database_url
engine = create_async_engine(DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
def setup_env():
    os.environ["ENVIRONMENT"] = "test"


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine_fixture():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # No teardown needed – each test recreates everything


@pytest_asyncio.fixture(scope="function")
async def session(db_engine_fixture):
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(session: AsyncSession):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
