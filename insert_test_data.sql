-- Insert test department
INSERT INTO departments (department_name) VALUES ('Human Resources');

-- Insert test shift
INSERT INTO shift_master (shift_name, shift_type, start_time, end_time, working_days) 
VALUES ('General Shift', 'Regular', '09:00:00', '18:00:00', 'Mon-Fri');

-- Insert test employee
INSERT INTO employees (employee_id, first_name, last_name, email_id, designation, department_id, shift_id) 
VALUES ('HR001', 'HR', 'Manager', 'hr@company.com', 'HR Manager', 1, 1);
