import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.api.database import Base, engine

@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

