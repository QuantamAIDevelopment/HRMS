-- Rohit Sharma (EMP001)
INSERT INTO payslips (
  id, company_name, company_address, company_phone, company_email,
  employee_name, employee_id, email, department, designation, annual_ctc, date_of_joining,
  month, year, basic_salary, hra, other_allowances, gross_earnings,
  pf_deduction, tax_deduction, other_deductions, total_deductions,
  net_pay, ytd_gross, ytd_deductions, ytd_net, ytd_net_total,
  basic_percentage, hra_percentage, pf_percentage,
  pdf_path, status, created_at
) VALUES
-- Nov 2024
(1, 'TechNova Pvt Ltd', 'HYD, Telangana, India', '+91-9876543210', 'hr@technova.com',
'Rohit Sharma','EMP001','rohit.sharma@technova.com','Engineering','Software Engineer',1200000,'2022-04-01',
11,2024,40000,20000,10000,70000,
4800,8000,200,13000,
57000,70000,13000,57000,57000,
40,50,12,'/files/payslips/2024/11/EMP001.pdf','Generated',NOW()),

-- Dec 2024
(2,'TechNova Pvt Ltd','HYD, Telangana, India','+91-9876543210','hr@technova.com',
'Rohit Sharma','EMP001','rohit.sharma@technova.com','Engineering','Software Engineer',1200000,'2022-04-01',
12,2024,40000,20000,10000,70000,
4800,8000,200,13000,
57000,140000,26000,114000,114000,
40,50,12,'/files/payslips/2024/12/EMP001.pdf','Generated',NOW()),

-- Jan 2025
(3,'TechNova Pvt Ltd','HYD, Telangana, India','+91-9876543210','hr@technova.com',
'Rohit Sharma','EMP001','rohit.sharma@technova.com','Engineering','Software Engineer',1200000,'2022-04-01',
1,2025,40000,20000,10000,70000,
4800,8000,200,13000,
57000,210000,39000,171000,171000,
40,50,12,'/files/payslips/2025/01/EMP001.pdf','Generated',NOW());
