-- Fix assets table to match the SQLAlchemy model
-- Add missing columns and update existing ones

-- Add employee_id column (if not exists)
ALTER TABLE assets ADD COLUMN IF NOT EXISTS employee_id VARCHAR(50);

-- Add assigned_to column (if not exists)
ALTER TABLE assets ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(50);

-- Add note column (if not exists)
ALTER TABLE assets ADD COLUMN IF NOT EXISTS note TEXT;

-- Update status constraint to include all valid statuses
ALTER TABLE assets DROP CONSTRAINT IF EXISTS assets_status_check;
ALTER TABLE assets ADD CONSTRAINT assets_status_check 
    CHECK (status IN ('Assigned', 'Available', 'Maintenance', 'Retired'));

-- Update condition constraint to include all valid conditions
ALTER TABLE assets DROP CONSTRAINT IF EXISTS assets_condition_check;
ALTER TABLE assets ADD CONSTRAINT assets_condition_check 
    CHECK (condition IN ('Excellent', 'Good', 'Fair', 'Poor') OR condition IS NULL);

-- Add foreign key for employee_id if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'assets_employee_id_fkey'
    ) THEN
        ALTER TABLE assets ADD CONSTRAINT assets_employee_id_fkey 
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE SET NULL;
    END IF;
END $$;

-- Migrate data from assigned_employee_id to employee_id if needed
UPDATE assets SET employee_id = assigned_employee_id WHERE employee_id IS NULL AND assigned_employee_id IS NOT NULL;

-- Optional: Drop the old assigned_employee_id column after migration (uncomment if you want to remove it)
-- ALTER TABLE assets DROP COLUMN IF EXISTS assigned_employee_id;
