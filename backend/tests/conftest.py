"""Pytest configuration and fixtures"""
import os
import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/insightforge_test"
)

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency"""
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(override_get_db) -> TestClient:
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client: TestClient, test_user: User) -> dict:
    """Get authentication headers for test user"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame for testing"""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "age": [25, 30, 35, 40, 45],
        "salary": [50000, 60000, 70000, 80000, 90000],
        "department": ["Engineering", "Sales", "Engineering", "HR", "Sales"]
    })


@pytest.fixture
def sample_sales_dataframe() -> pd.DataFrame:
    """Create a sample sales DataFrame for testing"""
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "product": ["Laptop", "Mouse", "Keyboard", "Monitor", "Laptop",
                   "Mouse", "Keyboard", "Monitor", "Laptop", "Mouse"],
        "quantity": [1, 2, 1, 1, 2, 3, 2, 1, 1, 4],
        "price": [1200.00, 25.00, 75.00, 300.00, 1200.00,
                 25.00, 75.00, 300.00, 1200.00, 25.00],
        "customer": ["Alice", "Bob", "Charlie", "David", "Alice",
                    "Bob", "Charlie", "David", "Eve", "Alice"]
    })


@pytest.fixture
def sample_customer_dataframe() -> pd.DataFrame:
    """Create a sample customer DataFrame for testing"""
    return pd.DataFrame({
        "customer_id": [1, 2, 3, 4, 5],
        "customer_name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "email": ["alice@example.com", "bob@example.com", "charlie@example.com",
                 "david@example.com", "eve@example.com"],
        "city": ["New York", "San Francisco", "Chicago", "Boston", "Seattle"],
        "total_orders": [5, 3, 2, 4, 1]
    })
