import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "HRMS Backend API"}

def test_get_policies():
    response = client.get("/api/standard-policy/")
    assert response.status_code == 200
    # Should return a list (empty or with policies)
    assert isinstance(response.json(), list)

def test_get_policy_by_name_standard():
    response = client.get("/api/standard-policy/by-name/Standard Policy")
    # This might return 404 if no policies exist, which is fine
    assert response.status_code in [200, 404]

def test_get_policy_by_name_flexible():
    response = client.get("/api/standard-policy/by-name/Flexible Policy")
    # This might return 404 if no policies exist, which is fine
    assert response.status_code in [200, 404]