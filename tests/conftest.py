import asyncio
import os
from collections.abc import AsyncIterator

# Force test DB URL before any app/db imports load the engine.
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("DATABASE_URL", TEST_DB_URL)
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
import re  # noqa: E402
from sqlalchemy import event  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.deps import get_current_user  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(TEST_DB_URL, future=True)
    
    @event.listens_for(eng.sync_engine, "connect")
    def sqlite_regexp(dbapi_connection, connection_record):
        def regexp(expr, item):
            if item is None:
                return False
            reg = re.compile(expr)
            return reg.search(item) is not None
        dbapi_connection.create_function("regexp", 2, regexp)

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db(session_factory) -> AsyncIterator[AsyncSession]:
    async with session_factory() as s:
        yield s


@pytest_asyncio.fixture
async def app(session_factory):
    from main import app as fastapi_app

    async def _override_get_db():
        async with session_factory() as s:
            yield s

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def authed_client(app, session_factory) -> AsyncIterator[AsyncClient]:
    """A client where authentication is bypassed and a synthetic user is injected."""
    async with session_factory() as s:
        user = User(
            nom="Test",
            prenom="Admin",
            email="admin.test@keyzonestates.tn",
            hashed_password="x",
            role=UserRole.CHEF_AGENCE,
            is_active=True,
        )
        s.add(user)
        await s.commit()
        await s.refresh(user)
        user_id = user.id

    async def _override_user():
        async with session_factory() as s:
            return await s.get(User, user_id)

    app.dependency_overrides[get_current_user] = _override_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def coordinator_client(app, session_factory) -> AsyncIterator[AsyncClient]:
    """A client with COORDINATEUR role."""
    async with session_factory() as s:
        user = User(
            nom="Coordinator",
            prenom="Test",
            email="coordinator.test@keyzonestates.tn",
            hashed_password="x",
            role=UserRole.COORDINATEUR,
            is_active=True,
        )
        s.add(user)
        await s.commit()
        await s.refresh(user)
        user_id = user.id

    async def _override_user():
        async with session_factory() as s:
            return await s.get(User, user_id)

    app.dependency_overrides[get_current_user] = _override_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def agent_client(app, session_factory) -> AsyncIterator[AsyncClient]:
    """A client with AGENT role."""
    async with session_factory() as s:
        user = User(
            nom="Agent",
            prenom="Test",
            email="agent.test@keyzonestates.tn",
            hashed_password="x",
            role=UserRole.AGENT,
            is_active=True,
        )
        s.add(user)
        await s.commit()
        await s.refresh(user)
        user_id = user.id

    async def _override_user():
        async with session_factory() as s:
            return await s.get(User, user_id)

    app.dependency_overrides[get_current_user] = _override_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
