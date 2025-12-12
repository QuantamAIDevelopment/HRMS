-- Migration: Add missing columns to employee_expenses table
-- Date: 2024

-- Add expense_code column
ALTER TABLE employee_expenses 
ADD COLUMN IF NOT EXISTS expense_code VARCHAR(20);

-- Add receipt_url column
ALTER TABLE employee_expenses 
ADD COLUMN IF NOT EXISTS receipt_url TEXT;

-- Update status column default if needed
ALTER TABLE employee_expenses 
ALTER COLUMN status SET DEFAULT 'PENDING';

-- Make description NOT NULL (if there are existing NULL values, update them first)
UPDATE employee_expenses SET description = '' WHERE description IS NULL;
ALTER TABLE employee_expenses 
ALTER COLUMN description SET NOT NULL;
