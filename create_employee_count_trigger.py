import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

try:
    # Create function to update employee count
    cur.execute("""
        CREATE OR REPLACE FUNCTION update_job_title_employee_count()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Update count for old designation (if changed)
            IF TG_OP = 'UPDATE' AND OLD.designation IS DISTINCT FROM NEW.designation THEN
                UPDATE job_titles 
                SET employees = (
                    SELECT COUNT(*) FROM employees 
                    WHERE designation = OLD.designation
                )
                WHERE job_title = OLD.designation;
            END IF;
            
            -- Update count for new/current designation
            IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                UPDATE job_titles 
                SET employees = (
                    SELECT COUNT(*) FROM employees 
                    WHERE designation = NEW.designation
                )
                WHERE job_title = NEW.designation;
            END IF;
            
            -- Update count for deleted designation
            IF TG_OP = 'DELETE' THEN
                UPDATE job_titles 
                SET employees = (
                    SELECT COUNT(*) FROM employees 
                    WHERE designation = OLD.designation
                )
                WHERE job_title = OLD.designation;
                RETURN OLD;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Drop existing trigger if exists
    cur.execute("DROP TRIGGER IF EXISTS employee_count_trigger ON employees")
    
    # Create trigger
    cur.execute("""
        CREATE TRIGGER employee_count_trigger
        AFTER INSERT OR UPDATE OR DELETE ON employees
        FOR EACH ROW EXECUTE FUNCTION update_job_title_employee_count();
    """)
    
    # Update current counts
    cur.execute("""
        UPDATE job_titles 
        SET employees = (
            SELECT COUNT(*) FROM employees 
            WHERE designation = job_titles.job_title
        );
    """)
    
    conn.commit()
    print("Employee count trigger created successfully")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

cur.close()
conn.close()