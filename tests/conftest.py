import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.models.base import Base
from src.models.session import get_db
from src.models.employee import Department, Employee

# Test database URL (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_department(db_session):
    """Create a sample department for testing"""
    department = Department(
        department_name="Engineering",
        description="Software Development Department"
    )
    db_session.add(department)
    db_session.commit()
    db_session.refresh(department)
    return department

@pytest.fixture
def sample_employee(db_session, sample_department):
    """Create a sample employee for testing"""
    employee = Employee(
        employee_id="EMP001",
        first_name="John",
        last_name="Doe",
        email_id="john.doe@company.com",
        phone_number="1234567890",
        joining_date="2023-01-15",
        designation="Software Developer",
        department_id=sample_department.id,
        reporting_manager="Jane Smith",
        annual_ctc=1200000.00
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee