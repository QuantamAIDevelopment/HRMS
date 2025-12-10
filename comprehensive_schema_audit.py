#!/usr/bin/env python3
"""
Comprehensive schema audit for all models in the HRMS system.
This script will identify all potential schema mismatches, missing columns, 
constraints, and relationship issues.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, text, inspect
from src.config.settings import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_database_tables():
    """Get all tables that exist in the database."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            
            return [row[0] for row in result.fetchall()]
            
    except Exception as e:
        logger.error(f"Error getting database tables: {e}")
        return []

def get_table_schema(table_name):
    """Get detailed schema information for a specific table."""
    try:
        sync_db_url = settings.sync_database_url
        engine = create_engine(sync_db_url)
        
        with engine.connect() as conn:
            # Get columns
            result = conn.execute(text(f"""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable, 
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """))
            
            columns = {}
            for row in result.fetchall():
                columns[row[0]] = {
                    'type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3],
                    'max_length': row[4]
                }
            
            # Get foreign keys
            result = conn.execute(text(f"""
                SELECT 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = '{table_name}'
            """))
            
            foreign_keys = {}
            for row in result.fetchall():
                foreign_keys[row[0]] = {
                    'references_table': row[1],
                    'references_column': row[2]
                }
            
            # Get indexes
            result = conn.execute(text(f"""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = '{table_name}'
                AND schemaname = 'public'
            """))
            
            indexes = [row[0] for row in result.fetchall()]
            
            return {
                'columns': columns,
                'foreign_keys': foreign_keys,
                'indexes': indexes
            }
            
    except Exception as e:
        logger.error(f"Error getting schema for {table_name}: {e}")
        return {'columns': {}, 'foreign_keys': {}, 'indexes': []}

def analyze_model_vs_database():
    """Analyze all SQLAlchemy models against database schema."""
    
    # Import all models to register them with SQLAlchemy
    try:
        from src.models.base import Base
        
        # Import all model files
        from src.models import (
            user, Employee_models, attendance, compliance_document,
            events_holidays, expense, hrms_models, job_title, leave,
            off_boarding, policy, salary, shift, timesheet
        )
        
        print("🔍 COMPREHENSIVE SCHEMA AUDIT")
        print("=" * 80)
        
        # Get all database tables
        db_tables = get_all_database_tables()
        print(f"\n📊 Found {len(db_tables)} tables in database:")
        for table in sorted(db_tables):
            print(f"  - {table}")
        
        # Get all SQLAlchemy models
        model_tables = {}
        for table_name, table_obj in Base.metadata.tables.items():
            model_tables[table_name] = table_obj
        
        print(f"\n🏗️ Found {len(model_tables)} models in SQLAlchemy:")
        for table in sorted(model_tables.keys()):
            print(f"  - {table}")
        
        # Find tables that exist in database but not in models
        db_only_tables = set(db_tables) - set(model_tables.keys())
        if db_only_tables:
            print(f"\n⚠️ Tables in database but NOT in models:")
            for table in sorted(db_only_tables):
                print(f"  - {table}")
        
        # Find models that don't have corresponding database tables
        model_only_tables = set(model_tables.keys()) - set(db_tables)
        if model_only_tables:
            print(f"\n⚠️ Models without corresponding database tables:")
            for table in sorted(model_only_tables):
                print(f"  - {table}")
        
        print(f"\n" + "=" * 80)
        print("🔍 DETAILED SCHEMA ANALYSIS")
        print("=" * 80)
        
        issues_found = []
        
        # Analyze each table that exists in both
        common_tables = set(db_tables) & set(model_tables.keys())
        
        for table_name in sorted(common_tables):
            print(f"\n📋 Analyzing table: {table_name}")
            print("-" * 50)
            
            # Get database schema
            db_schema = get_table_schema(table_name)
            db_columns = db_schema['columns']
            
            # Get SQLAlchemy model columns
            model_table = model_tables[table_name]
            model_columns = {}
            
            for column in model_table.columns:
                model_columns[column.name] = {
                    'type': str(column.type),
                    'nullable': column.nullable,
                    'default': column.default,
                    'foreign_key': column.foreign_keys
                }
            
            # Check for missing columns in database
            missing_in_db = set(model_columns.keys()) - set(db_columns.keys())
            if missing_in_db:
                print(f"  ❌ Columns in model but MISSING in database:")
                for col in sorted(missing_in_db):
                    print(f"    - {col} ({model_columns[col]['type']})")
                    issues_found.append(f"{table_name}.{col} - Missing in database")
            
            # Check for extra columns in database
            extra_in_db = set(db_columns.keys()) - set(model_columns.keys())
            if extra_in_db:
                print(f"  ⚠️ Columns in database but NOT in model:")
                for col in sorted(extra_in_db):
                    print(f"    - {col} ({db_columns[col]['type']})")
                    issues_found.append(f"{table_name}.{col} - Extra in database")
            
            # Check for type mismatches in common columns
            common_columns = set(model_columns.keys()) & set(db_columns.keys())
            for col_name in common_columns:
                model_col = model_columns[col_name]
                db_col = db_columns[col_name]
                
                # Check nullable mismatch
                if model_col['nullable'] != db_col['nullable']:
                    print(f"  ⚠️ Nullable mismatch in {col_name}:")
                    print(f"    Model: {model_col['nullable']}, DB: {db_col['nullable']}")
                    issues_found.append(f"{table_name}.{col_name} - Nullable mismatch")
            
            if not missing_in_db and not extra_in_db:
                print(f"  ✅ Schema matches perfectly!")
        
        # Summary
        print(f"\n" + "=" * 80)
        print("📊 AUDIT SUMMARY")
        print("=" * 80)
        
        if issues_found:
            print(f"\n❌ Found {len(issues_found)} schema issues:")
            for i, issue in enumerate(issues_found, 1):
                print(f"  {i}. {issue}")
        else:
            print(f"\n🎉 No schema issues found! All models match database schema.")
        
        return issues_found
        
    except Exception as e:
        logger.error(f"Error in model analysis: {e}")
        import traceback
        traceback.print_exc()
        return []

def generate_fix_suggestions(issues):
    """Generate SQL commands to fix identified issues."""
    if not issues:
        return
    
    print(f"\n" + "=" * 80)
    print("🔧 SUGGESTED FIXES")
    print("=" * 80)
    
    for issue in issues:
        if "Missing in database" in issue:
            table_col = issue.split(" - ")[0]
            table_name, col_name = table_col.split(".")
            print(f"\n-- Fix for {table_col}")
            print(f"ALTER TABLE {table_name} ADD COLUMN {col_name} VARCHAR(255);")
        
        elif "Extra in database" in issue:
            table_col = issue.split(" - ")[0]
            table_name, col_name = table_col.split(".")
            print(f"\n-- Consider removing {table_col} from model or database")
            print(f"-- ALTER TABLE {table_name} DROP COLUMN {col_name};")

def main():
    """Main function."""
    print("🚀 Starting comprehensive schema audit...\n")
    
    issues = analyze_model_vs_database()
    generate_fix_suggestions(issues)
    
    print(f"\n" + "=" * 80)
    print("✅ Schema audit completed!")
    print("=" * 80)

if __name__ == "__main__":
    main()