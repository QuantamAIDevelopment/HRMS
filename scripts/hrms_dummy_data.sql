-- HRMS Dummy Data SQL Script
-- Generated from Python dummy data generator
-- Execute this script to populate the database with test data

-- Clear existing data
DELETE FROM employee_expenses;
DELETE FROM payroll_setup;
DELETE FROM time_entries;
DELETE FROM compliance_documents_and_policy_management;
DELETE FROM events_holidays;
DELETE FROM policy_master;
DELETE FROM attendance;
DELETE FROM assets;
DELETE FROM leave_management;
DELETE FROM onboarding_process;
DELETE FROM employee_documents;
DELETE FROM educational_qualifications;
DELETE FROM employee_work_experience;
DELETE FROM bank_details;
DELETE FROM employee_personal_details;
DELETE FROM users;
DELETE FROM employees;
DELETE FROM job_titles;
DELETE FROM shift_master;
DELETE FROM departments;

-- Reset sequences
ALTER SEQUENCE departments_department_id_seq RESTART WITH 1;
ALTER SEQUENCE shift_master_shift_id_seq RESTART WITH 1;
ALTER SEQUENCE job_titles_job_title_id_seq RESTART WITH 1;
ALTER SEQUENCE users_id_seq RESTART WITH 1;

-- 1. Insert Departments
INSERT INTO departments (department_name, created_at, updated_at) VALUES
('Engineering', NOW(), NOW()),
('Human Resources', NOW(), NOW()),
('Finance', NOW(), NOW()),
('Marketing', NOW(), NOW()),
('Sales', NOW(), NOW()),
('Operations', NOW(), NOW()),
('IT Support', NOW(), NOW()),
('Quality Assurance', NOW(), NOW());

-- 2. Insert Shift Masters
INSERT INTO shift_master (shift_name, shift_type, start_time, end_time, working_days, created_at, updated_at) VALUES
('Day Shift', 'Regular', '09:00:00', '18:00:00', 'Monday-Friday', NOW(), NOW()),
('Night Shift', 'Regular', '22:00:00', '06:00:00', 'Monday-Friday', NOW(), NOW()),
('Flexible', 'Flexible', '10:00:00', '19:00:00', 'Monday-Friday', NOW(), NOW()),
('Weekend Shift', 'Weekend', '09:00:00', '17:00:00', 'Saturday-Sunday', NOW(), NOW());

-- 3. Insert Job Titles
INSERT INTO job_titles (job_title, job_description, department, level, salary_min, salary_max, created_at, updated_at) VALUES
('Software Engineer', 'Develop and maintain software applications', 'Engineering', 'Junior', 50000.00, 80000.00, NOW(), NOW()),
('Senior Software Engineer', 'Lead software development projects', 'Engineering', 'Senior', 80000.00, 120000.00, NOW(), NOW()),
('HR Manager', 'Manage human resources operations', 'Human Resources', 'Manager', 70000.00, 100000.00, NOW(), NOW()),
('HR Executive', 'Handle HR administrative tasks', 'Human Resources', 'Executive', 40000.00, 60000.00, NOW(), NOW()),
('Finance Manager', 'Oversee financial operations', 'Finance', 'Manager', 80000.00, 120000.00, NOW(), NOW()),
('Marketing Specialist', 'Execute marketing campaigns', 'Marketing', 'Specialist', 45000.00, 70000.00, NOW(), NOW()),
('Sales Representative', 'Generate sales and manage client relationships', 'Sales', 'Representative', 40000.00, 65000.00, NOW(), NOW()),
('QA Engineer', 'Test software applications for quality assurance', 'Quality Assurance', 'Engineer', 45000.00, 75000.00, NOW(), NOW());

-- 4. Insert Employees (Managers first)
INSERT INTO employees (employee_id, first_name, last_name, department_id, designation, joining_date, email_id, phone_number, location, shift_id, employee_type, annual_leaves, created_at, updated_at) VALUES
('EMP001', 'John', 'Manager', 1, 'HR Manager', '2023-01-15', 'john.manager@company.com', '+1-555-0101', 'New York', 1, 'Manager', 21, NOW(), NOW()),
('EMP002', 'Sarah', 'Executive', 1, 'HR Executive', '2023-02-20', 'sarah.executive@company.com', '+1-555-0102', 'Boston', 1, 'Executive', 21, NOW(), NOW()),
('EMP003', 'Mike', 'TeamLead', 2, 'Team Lead', '2023-03-10', 'mike.teamlead@company.com', '+1-555-0103', 'Chicago', 1, 'Team Lead', 21, NOW(), NOW()),
('EMP004', 'Lisa', 'Manager', 3, 'Finance Manager', '2023-04-05', 'lisa.manager@company.com', '+1-555-0104', 'San Francisco', 1, 'Manager', 21, NOW(), NOW());

-- Insert Regular Employees
INSERT INTO employees (employee_id, first_name, last_name, department_id, designation, joining_date, reporting_manager, email_id, phone_number, location, shift_id, employee_type, annual_leaves, created_at, updated_at) VALUES
('EMP005', 'Alice', 'Johnson', 2, 'Software Engineer', '2023-05-01', 'EMP003', 'alice.johnson@company.com', '+1-555-0105', 'Seattle', 1, 'Employee', 21, NOW(), NOW()),
('EMP006', 'Bob', 'Smith', 2, 'Senior Software Engineer', '2023-06-15', 'EMP003', 'bob.smith@company.com', '+1-555-0106', 'Portland', 2, 'Employee', 21, NOW(), NOW()),
('EMP007', 'Carol', 'Davis', 4, 'Marketing Specialist', '2023-07-20', 'EMP001', 'carol.davis@company.com', '+1-555-0107', 'Denver', 1, 'Employee', 21, NOW(), NOW()),
('EMP008', 'David', 'Wilson', 5, 'Sales Representative', '2023-08-10', 'EMP004', 'david.wilson@company.com', '+1-555-0108', 'Austin', 3, 'Employee', 21, NOW(), NOW()),
('EMP009', 'Emma', 'Brown', 8, 'QA Engineer', '2023-09-05', 'EMP003', 'emma.brown@company.com', '+1-555-0109', 'Miami', 1, 'Employee', 21, NOW(), NOW()),
('EMP010', 'Frank', 'Miller', 2, 'Software Engineer', '2023-10-12', 'EMP003', 'frank.miller@company.com', '+1-555-0110', 'Phoenix', 4, 'Employee', 21, NOW(), NOW());

-- 5. Insert Users for Authentication
INSERT INTO users (employee_id, email, full_name, role, hashed_password, is_active, created_at, updated_at) VALUES
('EMP001', 'john.manager@company.com', 'John Manager', 'Manager', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVrqUm/pW', true, NOW(), NOW()),
('EMP002', 'sarah.executive@company.com', 'Sarah Executive', 'Executive', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVrqUm/pW', true, NOW(), NOW()),
('EMP003', 'mike.teamlead@company.com', 'Mike TeamLead', 'Team Lead', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVrqUm/pW', true, NOW(), NOW()),
('EMP004', 'lisa.manager@company.com', 'Lisa Manager', 'Manager', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVrqUm/pW', true, NOW(), NOW()),
('EMP005', 'alice.johnson@company.com', 'Alice Johnson', 'Employee', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVrqUm/pW', true, NOW(), NOW()),
('EMP006', 'bob.smith@company.com', 'Bob Smith', 'Employee', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVrqUm/pW', true, NOW(), NOW());

-- 6. Insert Employee Personal Details
INSERT INTO employee_personal_details (employee_id, date_of_birth, gender, marital_status, blood_group, nationality, employee_email, employee_phone, employee_alternate_phone, employee_address, emergency_full_name, emergency_relationship, emergency_primary_phone, emergency_alternate_phone, emergency_address, created_at, updated_at) VALUES
('EMP001', '1985-03-15', 'Male', 'Married', 'O+', 'American', 'john.manager@company.com', '+1-555-0101', '+1-555-0201', '123 Main St, New York, NY 10001', 'Jane Manager', 'Spouse', '+1-555-0301', '+1-555-0401', '123 Main St, New York, NY 10001', NOW(), NOW()),
('EMP002', '1988-07-22', 'Female', 'Single', 'A+', 'American', 'sarah.executive@company.com', '+1-555-0102', '+1-555-0202', '456 Oak Ave, Boston, MA 02101', 'Robert Executive', 'Father', '+1-555-0302', '+1-555-0402', '456 Oak Ave, Boston, MA 02101', NOW(), NOW()),
('EMP003', '1982-11-08', 'Male', 'Married', 'B+', 'American', 'mike.teamlead@company.com', '+1-555-0103', '+1-555-0203', '789 Pine St, Chicago, IL 60601', 'Michelle TeamLead', 'Spouse', '+1-555-0303', '+1-555-0403', '789 Pine St, Chicago, IL 60601', NOW(), NOW()),
('EMP004', '1986-05-30', 'Female', 'Divorced', 'AB+', 'American', 'lisa.manager@company.com', '+1-555-0104', '+1-555-0204', '321 Elm Dr, San Francisco, CA 94101', 'Mark Manager', 'Brother', '+1-555-0304', '+1-555-0404', '321 Elm Dr, San Francisco, CA 94101', NOW(), NOW()),
('EMP005', '1990-09-12', 'Female', 'Single', 'O-', 'American', 'alice.johnson@company.com', '+1-555-0105', '+1-555-0205', '654 Cedar Ln, Seattle, WA 98101', 'Tom Johnson', 'Father', '+1-555-0305', '+1-555-0405', '654 Cedar Ln, Seattle, WA 98101', NOW(), NOW()),
('EMP006', '1987-12-03', 'Male', 'Married', 'A-', 'American', 'bob.smith@company.com', '+1-555-0106', '+1-555-0206', '987 Birch Rd, Portland, OR 97201', 'Susan Smith', 'Spouse', '+1-555-0306', '+1-555-0406', '987 Birch Rd, Portland, OR 97201', NOW(), NOW());

-- 7. Insert Bank Details
INSERT INTO bank_details (employee_id, account_number, account_holder_name, ifsc_code, bank_name, branch, account_type, pan_number, aadhaar_number, created_at, updated_at) VALUES
('EMP001', '1234567890123456', 'John Manager', 'HDFC0001234', 'HDFC Bank', 'New York Branch', 'Savings', 'ABCDE1234F', '123456789012', NOW(), NOW()),
('EMP002', '2345678901234567', 'Sarah Executive', 'ICIC0001234', 'ICICI Bank', 'Boston Branch', 'Savings', 'BCDEF2345G', '234567890123', NOW(), NOW()),
('EMP003', '3456789012345678', 'Mike TeamLead', 'SBIN0001234', 'State Bank of India', 'Chicago Branch', 'Current', 'CDEFG3456H', '345678901234', NOW(), NOW()),
('EMP004', '4567890123456789', 'Lisa Manager', 'AXIS0001234', 'Axis Bank', 'San Francisco Branch', 'Savings', 'DEFGH4567I', '456789012345', NOW(), NOW()),
('EMP005', '5678901234567890', 'Alice Johnson', 'HDFC0001234', 'HDFC Bank', 'Seattle Branch', 'Savings', 'EFGHI5678J', '567890123456', NOW(), NOW()),
('EMP006', '6789012345678901', 'Bob Smith', 'ICIC0001234', 'ICICI Bank', 'Portland Branch', 'Current', 'FGHIJ6789K', '678901234567', NOW(), NOW());

-- 8. Insert Sample Assets
INSERT INTO assets (serial_number, asset_name, asset_type, assigned_employee_id, status, condition, purchase_date, value, created_at, updated_at) VALUES
('SN12345001', 'Dell Laptop', 'Hardware', 'EMP001', 'Assigned', 'Good', '2023-01-15', 75000.00, NOW(), NOW()),
('SN12345002', 'HP Monitor', 'Hardware', 'EMP002', 'Assigned', 'Excellent', '2023-02-20', 25000.00, NOW(), NOW()),
('SN12345003', 'MacBook Pro', 'Hardware', 'EMP003', 'Assigned', 'Good', '2023-03-10', 120000.00, NOW(), NOW()),
('SN12345004', 'iPhone 14', 'Hardware', 'EMP004', 'Assigned', 'Excellent', '2023-04-05', 80000.00, NOW(), NOW()),
('SN12345005', 'Wireless Mouse', 'Hardware', NULL, 'Available', 'Good', '2023-05-01', 2500.00, NOW(), NOW()),
('SN12345006', 'Keyboard', 'Hardware', 'EMP005', 'Assigned', 'Fair', '2023-06-15', 3500.00, NOW(), NOW());

-- 9. Insert Policy Master
INSERT INTO policy_master (id, name, description, working_hours_per_day, working_days_per_week, is_active, grace_period_minutes, mark_late_after_minutes, half_day_hours, auto_deduct_for_absence, overtime_enabled, overtime_multiplier_weekdays, overtime_multiplier_weekend, require_check_in, require_check_out, created_at, updated_at) VALUES
(gen_random_uuid(), 'Standard Work Policy', 'Standard 8-hour work policy with flexible timing', 8.0, 5, true, 15, 30, 4.0, true, true, 1.5, 2.0, true, true, NOW(), NOW()),
(gen_random_uuid(), 'Flexible Work Policy', 'Flexible work hours with core working time', 8.0, 5, false, 30, 60, 4.0, false, true, 1.5, 2.0, true, true, NOW(), NOW());

-- 10. Insert Sample Attendance Records (Last 7 days)
INSERT INTO attendance (employee_id, attendance_date, punch_in, punch_out, work_hours, status, created_at, updated_at) VALUES
('EMP001', CURRENT_DATE - INTERVAL '1 day', '09:00:00', '18:00:00', 8.0, 'Present', NOW(), NOW()),
('EMP001', CURRENT_DATE - INTERVAL '2 days', '09:15:00', '18:15:00', 8.0, 'Late', NOW(), NOW()),
('EMP002', CURRENT_DATE - INTERVAL '1 day', '09:30:00', '18:30:00', 8.0, 'Present', NOW(), NOW()),
('EMP003', CURRENT_DATE - INTERVAL '1 day', '10:00:00', '19:00:00', 8.0, 'Present', NOW(), NOW()),
('EMP004', CURRENT_DATE - INTERVAL '1 day', NULL, NULL, 0.0, 'Absent', NOW(), NOW()),
('EMP005', CURRENT_DATE - INTERVAL '1 day', '09:00:00', '13:00:00', 4.0, 'Half Day', NOW(), NOW());

-- 11. Insert Sample Leave Records
INSERT INTO leave_management (employee_id, leave_type, start_date, end_date, employee_used_leaves, reason, status, created_at, updated_at) VALUES
('EMP001', 'Casual Leave', '2024-12-20', '2024-12-22', 3, 'Personal work', 'Pending', NOW(), NOW()),
('EMP002', 'Sick Leave', '2024-12-15', '2024-12-16', 2, 'Fever and cold', 'Approved', NOW(), NOW()),
('EMP003', 'Earned Leave', '2024-12-25', '2024-12-31', 7, 'Year end vacation', 'Pending', NOW(), NOW()),
('EMP005', 'Casual Leave', '2024-12-18', '2024-12-19', 2, 'Family function', 'Approved', NOW(), NOW());

-- 12. Insert Sample Payroll Setup
INSERT INTO payroll_setup (employee_id, designation, pay_cycle, basic_salary, hra, allowance, provident_fund_percentage, professional_tax, total_earnings, total_deductions, net_salary, month, basic_salary_type, hra_type, allowance_type, provident_fund_type, professional_tax_type, salary_components, organization_name, created_at, updated_at) VALUES
('EMP001', 'HR Manager', 'Monthly', 60000.00, 24000.00, 10000.00, 12.00, 200.00, 94000.00, 7400.00, 86600.00, 'December', 'Fixed', 'Percentage', 'Fixed', 'Percentage', 'Fixed', '{"earnings": {"basic": 60000, "hra": 24000}, "deductions": {"pf": 7200}}', 'HRMS Company', NOW(), NOW()),
('EMP002', 'HR Executive', 'Monthly', 45000.00, 18000.00, 8000.00, 12.00, 200.00, 71000.00, 5600.00, 65400.00, 'December', 'Fixed', 'Percentage', 'Fixed', 'Percentage', 'Fixed', '{"earnings": {"basic": 45000, "hra": 18000}, "deductions": {"pf": 5400}}', 'HRMS Company', NOW(), NOW()),
('EMP003', 'Team Lead', 'Monthly', 70000.00, 28000.00, 12000.00, 12.00, 200.00, 110000.00, 8600.00, 101400.00, 'December', 'Fixed', 'Percentage', 'Fixed', 'Percentage', 'Fixed', '{"earnings": {"basic": 70000, "hra": 28000}, "deductions": {"pf": 8400}}', 'HRMS Company', NOW(), NOW());

-- 13. Insert Sample Expenses
INSERT INTO employee_expenses (expense_code, employee_id, category, description, amount, expense_date, receipt_url, status, created_at, updated_at) VALUES
('EXP001001', 'EMP001', 'Travel', 'Business trip to client location', 2500.00, '2024-12-10', 'ZHVtbXlfcmVjZWlwdF9kYXRh', 'PENDING', NOW(), NOW()),
('EXP002001', 'EMP002', 'Food', 'Team lunch meeting', 1200.00, '2024-12-12', 'ZHVtbXlfcmVjZWlwdF9kYXRh', 'APPROVED', NOW(), NOW()),
('EXP003001', 'EMP003', 'Transportation', 'Taxi for client meeting', 800.00, '2024-12-14', 'ZHVtbXlfcmVjZWlwdF9kYXRh', 'REJECTED', NOW(), NOW()),
('EXP005001', 'EMP005', 'Office Supplies', 'Stationery for project', 500.00, '2024-12-11', 'ZHVtbXlfcmVjZWlwdF9kYXRh', 'APPROVED', NOW(), NOW());

-- 14. Insert Sample Time Entries
INSERT INTO time_entries (time_entry_id, employee_id, entry_date, project, task_description, hours, status, approver_id, approver_type, created_at, updated_at) VALUES
('TE12345001', 'EMP005', '2024-12-15', 'Project Alpha', 'Implemented user authentication module', 8.0, 'PENDING_MANAGER_APPROVAL', 'EMP003', 'MANAGER', NOW(), NOW()),
('TE12345002', 'EMP006', '2024-12-15', 'Project Beta', 'Fixed database connection issues', 6.5, 'APPROVED', 'EMP003', 'MANAGER', NOW(), NOW()),
('TE12345003', 'EMP005', '2024-12-14', 'Project Alpha', 'Code review and testing', 7.0, 'APPROVED', 'EMP003', 'MANAGER', NOW(), NOW()),
('TE12345004', 'EMP009', '2024-12-15', 'Project Gamma', 'Quality assurance testing', 8.0, 'PENDING_MANAGER_APPROVAL', 'EMP003', 'MANAGER', NOW(), NOW());

-- 15. Insert Sample Events and Holidays
INSERT INTO events_holidays (title, subtitle, type, event_date, location, created_at, updated_at) VALUES
('New Year Holiday', 'Company holiday', 'Holiday', '2025-01-01', 'All Offices', NOW(), NOW()),
('Team Building Event', 'Annual team building activity', 'Company Event', '2024-12-28', 'Conference Hall', NOW(), NOW()),
('Christmas Holiday', 'Christmas celebration', 'Holiday', '2024-12-25', 'All Offices', NOW(), NOW()),
('Training Session', 'Technical skills training', 'Training', '2024-12-30', 'Training Room A', NOW(), NOW());

-- Test Login Credentials (All passwords are: password123)
-- Email: john.manager@company.com | Password: password123
-- Email: sarah.executive@company.com | Password: password123  
-- Email: mike.teamlead@company.com | Password: password123
-- Email: lisa.manager@company.com | Password: password123