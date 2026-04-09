# reset_db.py
# This script performs a total reset of the time_travel.db database.
# Step 1: Delete the physical .db file to clear all existing records.
# Step 2: Re-run Time_Travel_db.py to recreate the schema and reference data from scratch.

import os
import subprocess

# Path to the SQLite database file (str)
db_file = "time_travel.db"

print("Starting database reset...")

# 1. Attempt to delete the existing database file using os.remove()
# os.path.exists() checks if the file is present before trying to delete it
if os.path.exists(db_file):
    try:
        # Delete the file entirely so the next step starts with a clean slate
        os.remove(db_file)
        print(f"Deleted existing database: {db_file}")
    except PermissionError:
        # File is locked (e.g. Streamlit app is running and has it open)
        print(f"⚠️ Warning: Cannot delete '{db_file}' because it is in use (probably by the Streamlit app).")
        print("   Proceeding with a 'Soft Reset' (dropping all tables inside the file instead)...")
        # We don't exit here — Time_Travel_db.py handles dropping tables internally
    except Exception as e:
        # Any other unexpected error: print and abort
        print(f"Error deleting database: {e}")
        exit(1)
else:
    # File doesn't exist yet, nothing to delete
    print(f"Database '{db_file}' does not exist yet. Proceeding.")

# 2. Run the database setup script to recreate the schema and reference data
# subprocess.run() executes Time_Travel_db.py as a child process
# capture_output=True captures stdout/stderr so we can print them here
print("Recreating database from 'Time_Travel_db.py'...")
try:
    result = subprocess.run(["python", "Time_Travel_db.py"], capture_output=True, text=True)
    # returncode == 0 means the script executed without errors
    if result.returncode == 0:
        print("Database successfully recreated!")
    else:
        # Non-zero return code signals a failure in the child process
        print("Error recreating database.")
        print(result.stderr)
except Exception as e:
    # Could not launch the subprocess at all (e.g. Python not in PATH)
    print(f"Failed to run 'Time_Travel_db.py': {e}")
