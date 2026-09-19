from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from taskforge.db import make_session_factory
from taskforge.models import Base
from taskforge.repository import TaskRepository
from taskforge.services import TaskService


@pytest.fixture()
def session_factory(tmp_path) -> Iterator[sessionmaker[Session]]:
    """A brand-new SQLite database per test, in pytest's temp directory."""
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", future=True)
    Base.metadata.create_all(engine)
    yield make_session_factory(engine)
    engine.dispose()


@pytest.fixture()
def session(session_factory) -> Iterator[Session]:
    db_session = session_factory()
    yield db_session
    db_session.close()


@pytest.fixture()
def repo(session) -> TaskRepository:
    return TaskRepository(session)


@pytest.fixture()
def service(repo) -> TaskService:
    return TaskService(repo)
