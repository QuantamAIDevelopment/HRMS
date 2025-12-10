import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.session import engine
from models.base import Base

# Force refresh metadata
Base.metadata.clear()
Base.metadata.reflect(bind=engine)

print("Metadata refreshed")

# Check if user_id has autoincrement
users_table = Base.metadata.tables.get('users')
if users_table is not None:
    user_id_col = users_table.columns.get('user_id')
    if user_id_col is not None:
        print(f"user_id autoincrement: {user_id_col.autoincrement}")
        print(f"user_id server_default: {user_id_col.server_default}")
    else:
        print("user_id column not found")
else:
    print("users table not found in metadata")
    print(f"Available tables: {list(Base.metadata.tables.keys())}")