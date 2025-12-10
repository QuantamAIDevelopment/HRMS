import pytest
from fastapi import status

def test_get_employees_list(client, sample_employee):
    """Test GET /employees endpoint"""
    response = client.get("/api/v1/employees")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "total_employees" in data
    assert "department_count" in data
    assert "new_joiners" in data
    assert "employees" in data
    assert "page" in data
    assert "size" in data
    
    assert data["total_employees"] == 1
    assert len(data["employees"]) == 1
    
    employee = data["employees"][0]
    assert employee["employee_id"] == "EMP001"
    assert employee["full_name"] == "John Doe"
    assert employee["email_id"] == "john.doe@company.com"

def test_get_employees_with_search(client, sample_employee):
    """Test GET /employees with search parameter"""
    response = client.get("/api/v1/employees?search=John")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["employees"]) == 1
    
    # Test search with no results
    response = client.get("/api/v1/employees?search=NonExistent")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["employees"]) == 0

def test_get_employees_with_department_filter(client, sample_employee, sample_department):
    """Test GET /employees with department filter"""
    response = client.get(f"/api/v1/employees?department_id={sample_department.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["employees"]) == 1

def test_get_employees_pagination(client, sample_employee):
    """Test GET /employees pagination"""
    response = client.get("/api/v1/employees?page=1&size=10")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 10

def test_get_employee_detail(client, sample_employee):
    """Test GET /employees/{employee_id} endpoint"""
    response = client.get(f"/api/v1/employees/{sample_employee.employee_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["employee_id"] == sample_employee.employee_id
    assert data["full_name"] == "John Doe"
    assert data["email_id"] == sample_employee.email_id
    assert "department" in data
    assert "leave_balances" in data

def test_get_employee_detail_not_found(client):
    """Test GET /employees/{employee_id} with non-existent employee"""
    response = client.get("/api/v1/employees/NONEXISTENT")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_employee(client, sample_employee):
    """Test PUT /employees/{employee_id} endpoint"""
    update_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "designation": "Senior Developer"
    }
    
    response = client.put(
        f"/api/v1/employees/{sample_employee.employee_id}",
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["designation"] == "Senior Developer"

def test_update_employee_email_conflict(client, sample_employee, db_session):
    """Test PUT /employees/{employee_id} with duplicate email"""
    # Create another employee
    from src.models.employee import Employee
    another_employee = Employee(
        employee_id="EMP002",
        first_name="Alice",
        last_name="Johnson",
        email_id="alice@company.com",
        joining_date="2023-02-01",
        designation="Developer",
        department_id=sample_employee.department_id
    )
    db_session.add(another_employee)
    db_session.commit()
    
    # Try to update first employee with second employee's email
    update_data = {"email_id": "alice@company.com"}
    
    response = client.put(
        f"/api/v1/employees/{sample_employee.employee_id}",
        json=update_data
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_update_employee_not_found(client):
    """Test PUT /employees/{employee_id} with non-existent employee"""
    update_data = {"first_name": "Test"}
    
    response = client.put("/api/v1/employees/NONEXISTENT", json=update_data)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_departments(client, sample_department):
    """Test GET /departments endpoint"""
    response = client.get("/api/v1/departments")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["department_id"] == sample_department.id
    assert data[0]["department_name"] == sample_department.department_name