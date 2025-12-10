#!/usr/bin/env python3
"""
HRMS Dummy Data Generator
Generates comprehensive test data for all models in the HRMS system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from datetime import datetime, date, time, timedelta
from decimal import Decimal
import random
import uuid
import base64
from faker import Faker
from sqlalchemy.orm import Session
from models.session import SessionLocal
from models.hrms_models import *
from models.user import User
from models.salary import PayrollSetup
from models.expense import Expense
from core.security import get_password_hash

fake = Faker()

def create_dummy_data():
    db = SessionLocal()
    try:
        print("🚀 Starting HRMS dummy data generation...")
        
        # Clear existing data
        print("🧹 Clearing existing data...")
        db.query(Expense).delete()
        db.query(PayrollSetup).delete()
        db.query(TimeEntry).delete()
        db.query(ComplianceDocument).delete()
        db.query(EventHoliday).delete()
        db.query(PolicyMaster).delete()
        db.query(Attendance).delete()
        db.query(Asset).delete()
        db.query(LeaveManagement).delete()
        db.query(OnboardingProcess).delete()
        db.query(EmployeeDocument).delete()
        db.query(EducationalQualification).delete()
        db.query(EmployeeWorkExperience).delete()
        db.query(BankDetail).delete()
        db.query(EmployeePersonalDetail).delete()
        db.query(User).delete()
        db.query(Employee).delete()
        db.query(JobTitle).delete()
        db.query(ShiftMaster).delete()
        db.query(Department).delete()
        db.commit()

        # 1. Create Departments
        print("📁 Creating departments...")
        departments = [
            Department(department_name="Engineering"),
            Department(department_name="Human Resources"),
            Department(department_name="Finance"),
            Department(department_name="Marketing"),
            Department(department_name="Sales"),
            Department(department_name="Operations"),
            Department(department_name="IT Support"),
            Department(department_name="Quality Assurance")
        ]
        db.add_all(departments)
        db.commit()

        # 2. Create Shift Masters
        print("⏰ Creating shift masters...")
        shifts = [
            ShiftMaster(shift_name="Day Shift", shift_type="Regular", start_time=time(9, 0), end_time=time(18, 0), working_days="Monday-Friday"),
            ShiftMaster(shift_name="Night Shift", shift_type="Regular", start_time=time(22, 0), end_time=time(6, 0), working_days="Monday-Friday"),
            ShiftMaster(shift_name="Flexible", shift_type="Flexible", start_time=time(10, 0), end_time=time(19, 0), working_days="Monday-Friday"),
            ShiftMaster(shift_name="Weekend Shift", shift_type="Weekend", start_time=time(9, 0), end_time=time(17, 0), working_days="Saturday-Sunday")
        ]
        db.add_all(shifts)
        db.commit()

        # 3. Create Job Titles
        print("💼 Creating job titles...")
        job_titles = [
            JobTitle(job_title="Software Engineer", job_description="Develop and maintain software applications", department="Engineering", level="Junior", salary_min=Decimal("50000"), salary_max=Decimal("80000")),
            JobTitle(job_title="Senior Software Engineer", job_description="Lead software development projects", department="Engineering", level="Senior", salary_min=Decimal("80000"), salary_max=Decimal("120000")),
            JobTitle(job_title="HR Manager", job_description="Manage human resources operations", department="Human Resources", level="Manager", salary_min=Decimal("70000"), salary_max=Decimal("100000")),
            JobTitle(job_title="HR Executive", job_description="Handle HR administrative tasks", department="Human Resources", level="Executive", salary_min=Decimal("40000"), salary_max=Decimal("60000")),
            JobTitle(job_title="Finance Manager", job_description="Oversee financial operations", department="Finance", level="Manager", salary_min=Decimal("80000"), salary_max=Decimal("120000")),
            JobTitle(job_title="Marketing Specialist", job_description="Execute marketing campaigns", department="Marketing", level="Specialist", salary_min=Decimal("45000"), salary_max=Decimal("70000")),
            JobTitle(job_title="Sales Representative", job_description="Generate sales and manage client relationships", department="Sales", level="Representative", salary_min=Decimal("40000"), salary_max=Decimal("65000")),
            JobTitle(job_title="QA Engineer", job_description="Test software applications for quality assurance", department="Quality Assurance", level="Engineer", salary_min=Decimal("45000"), salary_max=Decimal("75000"))
        ]
        db.add_all(job_titles)
        db.commit()

        # 4. Create Employees
        print("👥 Creating employees...")
        employees = []
        employee_ids = []
        
        # Create managers first
        managers = [
            {"id": "EMP001", "name": "John Manager", "dept": 1, "role": "HR Manager", "type": "Manager"},
            {"id": "EMP002", "name": "Sarah Executive", "dept": 1, "role": "HR Executive", "type": "Executive"},
            {"id": "EMP003", "name": "Mike TeamLead", "dept": 2, "role": "Team Lead", "type": "Team Lead"},
            {"id": "EMP004", "name": "Lisa Manager", "dept": 3, "role": "Finance Manager", "type": "Manager"}
        ]
        
        for mgr in managers:
            names = mgr["name"].split()
            emp = Employee(
                employee_id=mgr["id"],
                first_name=names[0],
                last_name=" ".join(names[1:]),
                department_id=mgr["dept"],
                designation=mgr["role"],
                joining_date=fake.date_between(start_date='-2y', end_date='-6m'),
                email_id=f"{names[0].lower()}.{names[1].lower()}@company.com",
                phone_number=fake.phone_number()[:20],
                location=fake.city(),
                shift_id=1,
                employee_type=mgr["type"],
                annual_leaves=21
            )
            employees.append(emp)
            employee_ids.append(mgr["id"])

        # Create regular employees
        for i in range(5, 51):  # EMP005 to EMP050
            emp_id = f"EMP{i:03d}"
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            emp = Employee(
                employee_id=emp_id,
                first_name=first_name,
                last_name=last_name,
                department_id=random.randint(1, 8),
                designation=random.choice(["Software Engineer", "Senior Software Engineer", "Marketing Specialist", "Sales Representative", "QA Engineer"]),
                joining_date=fake.date_between(start_date='-3y', end_date='today'),
                reporting_manager=random.choice(["EMP001", "EMP003", "EMP004"]),
                email_id=f"{first_name.lower()}.{last_name.lower()}@company.com",
                phone_number=fake.phone_number()[:20],
                location=fake.city(),
                shift_id=random.randint(1, 4),
                employee_type="Employee",
                annual_leaves=21
            )
            employees.append(emp)
            employee_ids.append(emp_id)

        db.add_all(employees)
        db.commit()

        # 5. Create Users for Authentication
        print("🔐 Creating user accounts...")
        users = []
        for emp in employees[:10]:  # Create users for first 10 employees
            user = User(
                employee_id=emp.employee_id,
                email=emp.email_id,
                full_name=f"{emp.first_name} {emp.last_name}",
                role=emp.employee_type,
                hashed_password=get_password_hash("password123"),
                is_active=True
            )
            users.append(user)
        db.add_all(users)
        db.commit()

        print("✅ Dummy data generation completed successfully!")
        print(f"📊 Generated data summary:")
        print(f"   - Departments: {len(departments)}")
        print(f"   - Employees: {len(employees)}")
        print(f"   - Users: {len(users)}")
        
        print("\n🔑 Test Login Credentials:")
        print("   Email: john.manager@company.com | Password: password123")
        print("   Email: sarah.executive@company.com | Password: password123")
        print("   Email: mike.teamlead@company.com | Password: password123")

    except Exception as e:
        print(f"❌ Error generating dummy data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_dummy_data()