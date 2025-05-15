"""Test the api."""
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_health_api():
    """Checks the health api."""
    response = client.get("/health")
    assert (
        response.status_code == 200
    ), "Error, make sure the server is running correctly."
    assert response.json() == {
        "message": "response from the server",
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.DEV_MODE,
    }
