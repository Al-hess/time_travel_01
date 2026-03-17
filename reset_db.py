# reset_db.py
# This script performs a total reset of the time_travel.db database.
# 1. It deletes the physical .db file to clear all existing records.
# 2. It re-runs the schema creation script to start fresh with pre-populated values.

import os
import subprocess

# File path 
db_file = "time_travel.db"

print("Starting database reset...")

# 1. Attempt to delete the existing database file
if os.path.exists(db_file):
    try:
        os.remove(db_file)
        print(f"Deleted existing database: {db_file}")
    except PermissionError:
        print(f"⚠️ Warning: Cannot delete '{db_file}' because it is in use (probably by the Streamlit app).")
        print("   Proceeding with a 'Soft Reset' (dropping all tables inside the file instead)...")
        # We don't exit here anymore, because Time_Travel_db.py now drops tables itself.
    except Exception as e:
        print(f"Error deleting database: {e}")
        exit(1)
else:
    print(f"Database '{db_file}' does not exist yet. Proceeding.")

# 2. Run the database setup script (Time_Travel_db) to recreate it
print("Recreating database from 'Time_Travel_db.py'...")
try:
    result = subprocess.run(["python", "Time_Travel_db.py"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Database successfully recreated!")
    else:
        print("Error recreating database.")
        print(result.stderr)
except Exception as e:
    print(f"Failed to run 'Time_Travel_db.py': {e}")
