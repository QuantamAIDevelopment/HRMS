-- Add missing columns to payroll_setup table
ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS pdf_path VARCHAR(255);
ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS month VARCHAR(20);
ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS basic_salary_type VARCHAR(50);
ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS hra_type VARCHAR(50);
ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS allowance_type VARCHAR(50);
ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS provident_fund_type VARCHAR(50);
ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS professional_tax_type VARCHAR(50);
ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS salary_components JSONB;
ALTER TABLE payroll_setup ADD COLUMN IF NOT EXISTS organization_name VARCHAR(100);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_payroll_month ON payroll_setup(month);
CREATE INDEX IF NOT EXISTS idx_payroll_employee_id ON payroll_setup(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_month ON payroll_setup(employee_id, month);

-- Verify the changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'payroll_setup' 
ORDER BY ordinal_position;