"""
Add missing columns to employee_personal_details table
"""
from sqlalchemy import create_engine, text, inspect
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_columns():
    engine = create_engine(settings.database_url)
    
    # Define all columns that should exist
    required_columns = {
        'id': 'INTEGER PRIMARY KEY',
        'employee_id': 'VARCHAR(50) UNIQUE',
        'date_of_birth': 'DATE',
        'gender': 'VARCHAR(20)',
        'marital_status': 'VARCHAR(20)',
        'blood_group': 'VARCHAR(5)',
        'nationality': 'VARCHAR(50)',
        'employee_phone': 'VARCHAR(20)',
        'employee_email': 'VARCHAR(100)',
        'employee_alternate_phone': 'VARCHAR(20)',
        'employee_address': 'VARCHAR(255)',
        'city': 'VARCHAR(100)',
        'pincode': 'VARCHAR(20)',
        'country': 'VARCHAR(100)',
        'state': 'VARCHAR(100)',
        'emergency_full_name': 'VARCHAR(50)',
        'emergency_relationship': 'VARCHAR(50)',
        'emergency_primary_phone': 'VARCHAR(20)',
        'emergency_alternate_phone': 'VARCHAR(20)',
        'emergency_address': 'VARCHAR(150)',
        'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    }
    
    with engine.connect() as conn:
        # Get existing columns
        inspector = inspect(engine)
        existing_columns = [col['name'] for col in inspector.get_columns('employee_personal_details')]
        
        logger.info(f"Existing columns: {existing_columns}")
        
        # Find missing columns
        missing_columns = [col for col in required_columns.keys() if col not in existing_columns]
        
        if not missing_columns:
            logger.info("All columns already exist!")
            return
        
        logger.info(f"Missing columns: {missing_columns}")
        
        # Add missing columns
        for col_name in missing_columns:
            col_type = required_columns[col_name]
            try:
                alter_sql = f"ALTER TABLE employee_personal_details ADD COLUMN {col_name} {col_type}"
                logger.info(f"Executing: {alter_sql}")
                conn.execute(text(alter_sql))
                conn.commit()
                logger.info(f"✓ Added column: {col_name}")
            except Exception as e:
                logger.error(f"✗ Failed to add column {col_name}: {str(e)}")
        
        logger.info("Migration completed!")

if __name__ == "__main__":
    add_missing_columns()
