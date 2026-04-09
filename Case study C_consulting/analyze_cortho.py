import pandas as pd
import numpy as np

# Load the dataset
# Path: Case study C_consulting/Cortho.xls
file_path = r'Case study C_consulting/Cortho.xls'

try:
    df = pd.read_excel(file_path)
    print("Dataset loaded successfully.")
    print("\n--- First 5 rows ---")
    print(df.head())
    print("\n--- Column Info ---")
    print(df.info())
    print("\n--- Summary Statistics ---")
    print(df.describe())
    
    # Check for missing values
    print("\n--- Missing Values ---")
    print(df.isnull().sum())

    # Save a copy as CSV for easier access if needed
    df.to_csv('cortho_processed.csv', index=False)
except Exception as e:
    print(f"Error loading dataset: {e}")
