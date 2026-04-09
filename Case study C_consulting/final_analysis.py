import pandas as pd
import numpy as np

df = pd.read_csv('cortho_processed.csv')

print("\n--- Sales Aggregate ---")
print(f"Total Sales Current Year (SALESY): {df['SALESY'].sum():,.0f}")
print(f"Total Sales Previous Year (SALES12): {df['SALES12'].sum():,.0f}")
print(f"Total Growth: {df['SALESY'].sum() - df['SALES12'].sum():,.0f}")

# Correlation with SALESY
corrs = df.corr()['SALESY'].sort_values(ascending=False)
print("\n--- Top Correlations ---")
print(corrs.head(10))

# Regression-like analysis (Mean sales per surgery)
df['TOTAL_OPS'] = df['HIP'] + df['KNEE'] + df['FEMUR']
avg_sales_per_op = df[df['TOTAL_OPS'] > 0]['SALESY'].sum() / df[df['TOTAL_OPS'] > 0]['TOTAL_OPS'].sum()
print(f"\nAverage Sales per Operation: ${avg_sales_per_op:.2f}")

# Segments
print("\n--- Segment Analysis ---")
for t in ['TH', 'TRAUMA', 'REHAB']:
    res = df.groupby(t)['SALESY'].mean()
    print(f"Mean Sales by {t}:\n{res}")

# Identify Top 10 Growth Opportunities
# Hospitals with most TOTAL_OPS but 0 SALESY
opportunities = df[df['SALESY'] == 0].sort_values(by='TOTAL_OPS', ascending=False)
print("\n--- Top 10 Growth Opportunities (High Volume, Zero Sales) ---")
print(opportunities[['BEDS', 'TOTAL_OPS', 'TH', 'TRAUMA', 'REHAB']].head(10))

# Check hospitals where Sales increased
increased = df[df['SALESY'] > df['SALES12']]
print(f"\nNumber of hospitals where sales increased: {len(increased)}")
