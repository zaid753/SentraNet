import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.api.auth import get_current_user, get_current_workspace
from backend.api.models import User, Workspace
from backend.api.database import Base, engine

@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def override_auth_dependencies():
    user = User(id="test_user", email="test@example.com", name="Test User")
    workspace = Workspace(id="test_workspace", owner_id="test_user", name="Test Workspace")
    
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_current_workspace] = lambda: workspace
    
    yield
    
    app.dependency_overrides.clear()
