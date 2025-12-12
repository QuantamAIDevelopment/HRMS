import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_salary():
    salary_data = {
        "employee_id": "EMP001",
        "basic_salary": 50000,
        "allowances": 10000,
        "deductions": 5000,
        "pay_period": "Monthly"
    }
    response = client.post("/api/v1/salary", json=salary_data)
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == "EMP001"
    assert data["net_salary"] == 55000

def test_get_salary():
    response = client.get("/api/v1/salary/EMP001")
    assert response.status_code in [200, 404]