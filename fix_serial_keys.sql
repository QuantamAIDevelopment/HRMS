-- Fix primary keys to auto-increment as serial numbers

-- Job Titles table
ALTER TABLE job_titles ALTER COLUMN job_title_id SET DEFAULT nextval(pg_get_serial_sequence('job_titles', 'job_title_id'));
CREATE SEQUENCE IF NOT EXISTS job_titles_job_title_id_seq OWNED BY job_titles.job_title_id;
SELECT setval('job_titles_job_title_id_seq', COALESCE(MAX(job_title_id), 0) + 1, false) FROM job_titles;
ALTER TABLE job_titles ALTER COLUMN job_title_id SET DEFAULT nextval('job_titles_job_title_id_seq');

-- Shift Master table
ALTER TABLE shift_master ALTER COLUMN shift_id SET DEFAULT nextval(pg_get_serial_sequence('shift_master', 'shift_id'));
CREATE SEQUENCE IF NOT EXISTS shift_master_shift_id_seq OWNED BY shift_master.shift_id;
SELECT setval('shift_master_shift_id_seq', COALESCE(MAX(shift_id), 0) + 1, false) FROM shift_master;
ALTER TABLE shift_master ALTER COLUMN shift_id SET DEFAULT nextval('shift_master_shift_id_seq');

-- Departments table
ALTER TABLE departments ALTER COLUMN department_id SET DEFAULT nextval(pg_get_serial_sequence('departments', 'department_id'));
CREATE SEQUENCE IF NOT EXISTS departments_department_id_seq OWNED BY departments.department_id;
SELECT setval('departments_department_id_seq', COALESCE(MAX(department_id), 0) + 1, false) FROM departments;
ALTER TABLE departments ALTER COLUMN department_id SET DEFAULT nextval('departments_department_id_seq');

-- Events Holidays table
ALTER TABLE events_holidays ALTER COLUMN id SET DEFAULT nextval(pg_get_serial_sequence('events_holidays', 'id'));
CREATE SEQUENCE IF NOT EXISTS events_holidays_id_seq OWNED BY events_holidays.id;
SELECT setval('events_holidays_id_seq', COALESCE(MAX(id), 0) + 1, false) FROM events_holidays;
ALTER TABLE events_holidays ALTER COLUMN id SET DEFAULT nextval('events_holidays_id_seq');

-- Off Boarding table
ALTER TABLE off_boarding ALTER COLUMN id SET DEFAULT nextval(pg_get_serial_sequence('off_boarding', 'id'));
CREATE SEQUENCE IF NOT EXISTS off_boarding_id_seq OWNED BY off_boarding.id;
SELECT setval('off_boarding_id_seq', COALESCE(MAX(id), 0) + 1, false) FROM off_boarding;
ALTER TABLE off_boarding ALTER COLUMN id SET DEFAULT nextval('off_boarding_id_seq');

-- Time Entries table
ALTER TABLE time_entries ALTER COLUMN id SET DEFAULT nextval(pg_get_serial_sequence('time_entries', 'id'));
CREATE SEQUENCE IF NOT EXISTS time_entries_id_seq OWNED BY time_entries.id;
SELECT setval('time_entries_id_seq', COALESCE(MAX(id), 0) + 1, false) FROM time_entries;
ALTER TABLE time_entries ALTER COLUMN id SET DEFAULT nextval('time_entries_id_seq');

-- Assets table
ALTER TABLE assets ALTER COLUMN asset_id SET DEFAULT nextval(pg_get_serial_sequence('assets', 'asset_id'));
CREATE SEQUENCE IF NOT EXISTS assets_asset_id_seq OWNED BY assets.asset_id;
SELECT setval('assets_asset_id_seq', COALESCE(MAX(asset_id), 0) + 1, false) FROM assets;
ALTER TABLE assets ALTER COLUMN asset_id SET DEFAULT nextval('assets_asset_id_seq');

-- Bank Details table
ALTER TABLE bank_details ALTER COLUMN bank_id SET DEFAULT nextval(pg_get_serial_sequence('bank_details', 'bank_id'));
CREATE SEQUENCE IF NOT EXISTS bank_details_bank_id_seq OWNED BY bank_details.bank_id;
SELECT setval('bank_details_bank_id_seq', COALESCE(MAX(bank_id), 0) + 1, false) FROM bank_details;
ALTER TABLE bank_details ALTER COLUMN bank_id SET DEFAULT nextval('bank_details_bank_id_seq');