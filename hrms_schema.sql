-- ============================================================
-- HRMS - COMPLETE NORMALIZED DATABASE SCHEMA
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. DEPARTMENTS (LOOKUP)
-- ============================================================
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) UNIQUE NOT NULL
);

-- ============================================================
-- 2. SHIFT MASTER
-- ============================================================
CREATE TABLE shift_master (
    shift_id SERIAL PRIMARY KEY,
    shift_name VARCHAR(150) NOT NULL,
    shift_type VARCHAR(100) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    working_days VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- 3. EMPLOYEES (MASTER TABLE)
-- ============================================================
CREATE TABLE employees (
    employee_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    full_name VARCHAR GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
    department_id INT,
    designation VARCHAR(50),
    joining_date DATE,
    reporting_manager VARCHAR(50),
    email_id VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    location VARCHAR(50),
    shift_id INT,
    profile_photo VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (shift_id) REFERENCES shift_master(shift_id),
    FOREIGN KEY (reporting_manager) REFERENCES employees(employee_id)
);

CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_shift ON employees(shift_id);

-- ============================================================
-- 4. EMPLOYEE PERSONAL DETAILS
-- ============================================================
CREATE TABLE employee_personal_details (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    marital_status VARCHAR(20),
    blood_group VARCHAR(5),
    nationality VARCHAR(50),
    employee_email VARCHAR(50),
    employee_phone VARCHAR(20),
    employee_alternate_phone VARCHAR(20),
    employee_address VARCHAR(150),
    emergency_full_name VARCHAR(50),
    emergency_relationship VARCHAR(50),
    emergency_primary_phone VARCHAR(20),
    emergency_alternate_phone VARCHAR(20),
    emergency_address VARCHAR(150),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- ============================================================
-- 5. BANK DETAILS
-- ============================================================
CREATE TABLE bank_details (
    bank_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    account_number VARCHAR(30) UNIQUE,
    account_holder_name VARCHAR(50) NOT NULL,
    ifsc_code VARCHAR(20) NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    branch VARCHAR(150),
    account_type VARCHAR(20) CHECK (account_type IN ('Savings','Current')),
    pan_number VARCHAR(15),
    aadhaar_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- ============================================================
-- 6. ASSETS
-- ============================================================
CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    serial_number VARCHAR(50) UNIQUE,
    asset_name VARCHAR(50) NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    assigned_employee_id VARCHAR(50),
    status VARCHAR(50) CHECK (status IN ('Assigned','Available','Maintenance')) DEFAULT 'Available',
    condition VARCHAR(50) CHECK (condition IN ('Excellent','Good','Fair')) DEFAULT 'Good',
    purchase_date DATE,
    value NUMERIC(12,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (assigned_employee_id) REFERENCES employees(employee_id) ON DELETE SET NULL
);

CREATE INDEX idx_assets_employee ON assets(assigned_employee_id);

-- ============================================================
-- 7. ATTENDANCE
-- ============================================================
CREATE TABLE attendance (
    attendance_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    attendance_date DATE NOT NULL,
    punch_in TIME,
    punch_out TIME,
    work_hours NUMERIC(5,2),
    status VARCHAR(50),
    policy_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (policy_id) REFERENCES policy_master(id)
);

CREATE INDEX idx_attendance_emp ON attendance(employee_id);
CREATE INDEX idx_attendance_date ON attendance(attendance_date);

-- ============================================================
-- 8. EDUCATIONAL QUALIFICATIONS
-- ============================================================
CREATE TABLE educational_qualifications (
    edu_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    course_name VARCHAR(150) NOT NULL,
    institution_name VARCHAR(200) NOT NULL,
    specialization VARCHAR(50),
    start_year INT,
    end_year INT,
    grade VARCHAR(50),
    skill_name VARCHAR(150),
    proficiency_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX idx_edu_employee ON educational_qualifications(employee_id);

-- ============================================================
-- 9. EMPLOYEE DOCUMENTS
-- ============================================================
CREATE TABLE employee_documents (
    document_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    document_name VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    upload_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- ============================================================
-- 10. EMPLOYEE EXPENSES
-- ============================================================
CREATE TABLE employee_expenses (
    expense_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    amount NUMERIC(12,2) NOT NULL,
    expense_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- ============================================================
-- 11. PAYROLL SETUP
-- ============================================================
CREATE TABLE payroll_setup (
    payroll_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    pay_cycle VARCHAR(20) CHECK (pay_cycle IN ('Monthly','Weekly','Biweekly')) DEFAULT 'Monthly',
    basic_salary NUMERIC(12,2) DEFAULT 0,
    hra NUMERIC(12,2) DEFAULT 0,
    allowance NUMERIC(12,2) DEFAULT 0,
    bonus_percentage NUMERIC(5,2) DEFAULT 0,
    is_bonus_taxable BOOLEAN DEFAULT false,
    is_allowance_taxable BOOLEAN DEFAULT false,
    is_hra_taxable BOOLEAN DEFAULT false,
    is_basic_taxable BOOLEAN DEFAULT false,
    provident_fund_percentage NUMERIC(5,2) DEFAULT 0,
    professional_tax NUMERIC(12,2) DEFAULT 0,
    income_tax NUMERIC(12,2) DEFAULT 0,
    lop_amount NUMERIC(12,2) DEFAULT 0,
    is_pf_locked BOOLEAN DEFAULT false,
    is_pt_locked BOOLEAN DEFAULT false,
    is_income_tax_auto BOOLEAN DEFAULT false,
    total_earnings NUMERIC(12,2) DEFAULT 0,
    total_deductions NUMERIC(12,2) DEFAULT 0,
    net_salary NUMERIC(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- ============================================================
-- 12. LEAVE MANAGEMENT
-- ============================================================
CREATE TABLE leave_management (
    leave_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    leave_type VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- ============================================================
-- 13. ONBOARDING PROCESS
-- ============================================================
CREATE TABLE onboarding_process (
    onboarding_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    name VARCHAR(50) NOT NULL,
    position VARCHAR(50) NOT NULL,
    department VARCHAR(50) NOT NULL,
    joining_date DATE NOT NULL,
    shifts VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- ============================================================
-- 14. JOB TITLES
-- ============================================================
CREATE TABLE job_titles (
    job_title_id SERIAL PRIMARY KEY,
    job_title VARCHAR(150) NOT NULL,
    job_description TEXT NOT NULL,
    department VARCHAR(100) NOT NULL,
    level VARCHAR(50) NOT NULL,
    salary_min NUMERIC(10,2),
    salary_max NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- 15. TIME ENTRIES
-- ============================================================
CREATE TABLE time_entries (
    time_entry_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    entry_date DATE NOT NULL,
    project VARCHAR(150) NOT NULL,
    task_description TEXT NOT NULL,
    hours NUMERIC(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX idx_time_entry_employee ON time_entries(employee_id);
CREATE INDEX idx_time_entry_date ON time_entries(entry_date);

-- ============================================================
-- 16. COMPLIANCE DOCUMENTS AND POLICY MANAGEMENT
-- ============================================================
CREATE TABLE compliance_documents_and_policy_management (
    document_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) CHECK (category IN ('Policy','Compliance','Legal','Training')) NOT NULL,
    description TEXT,
    uploaded_document TEXT,
    uploaded_by VARCHAR(50) NOT NULL,
    uploaded_on TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (uploaded_by) REFERENCES employees(employee_id)
);

-- ============================================================
-- 17. POLICY MASTER
-- ============================================================
CREATE TABLE policy_master (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    working_hours_per_day FLOAT NOT NULL,
    working_days_per_week INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    grace_period_minutes INTEGER NOT NULL,
    mark_late_after_minutes INTEGER NOT NULL,
    half_day_hours FLOAT NOT NULL,
    auto_deduct_for_absence BOOLEAN NOT NULL,
    overtime_enabled BOOLEAN NOT NULL,
    overtime_multiplier_weekdays FLOAT,
    overtime_multiplier_weekend FLOAT,
    require_check_in BOOLEAN NOT NULL,
    require_check_out BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- END OF FILE
-- ============================================================
