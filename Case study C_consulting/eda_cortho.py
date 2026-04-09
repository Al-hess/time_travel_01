import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the processed data
df = pd.read_csv('cortho_processed.csv')

# 1. Sales Distribution
print("\n--- Sales Distribution (SALESY) ---")
print(df['SALESY'].describe())

# 2. Correlation Analysis
# We want to see what correlates most with SALESY
corrs = df.corr()['SALESY'].sort_values(ascending=False)
print("\n--- Correlation with SALESY ---")
print(corrs)

# 3. Sales by Hospital Type
# TH, TRAUMA, REHAB are 0/1
types = ['TH', 'TRAUMA', 'REHAB']
print("\n--- Sales by Hospital Type ---")
for t in types:
    summary = df.groupby(t)['SALESY'].agg(['mean', 'median', 'count', 'sum'])
    print(f"\nType: {t}")
    print(summary)

# 4. Sales Growth
df['SALES_GROWTH'] = df['SALESY'] - df['SALES12']
print("\n--- Sales Growth Statistics ---")
print(df['SALES_GROWTH'].describe())

# 5. Surgical Volume vs Sales
# Total operations current year
df['TOTAL_OPS'] = df['HIP'] + df['KNEE'] + df['FEMUR']
print("\n--- Total Operations vs Sales Correlation ---")
print(df[['TOTAL_OPS', 'SALESY']].corr().iloc[0, 1])

# 6. Identifying "Low Penetration" High-Volume Hospitals
# Defined as high surgery volume but low sales
# Let's look at hospitals in the top 25% for operations but bottom 25% for sales
high_ops_thresh = df['TOTAL_OPS'].quantile(0.75)
low_sales_thresh = df['SALESY'].quantile(0.25)

underpenetrated = df[(df['TOTAL_OPS'] >= high_ops_thresh) & (df['SALESY'] <= low_sales_thresh)]
print(f"\n--- Underpenetrated Hospitals (High Ops, Low Sales) ---")
print(f"Count: {len(underpenetrated)}")
print(underpenetrated[['BEDS', 'TOTAL_OPS', 'SALESY', 'TH', 'TRAUMA']].head(10))

# 7. Efficiency - Sales per Bed
df['SALES_PER_BED'] = df['SALESY'] / df['BEDS'].replace(0, np.nan)
print("\n--- Sales per Bed ---")
print(df['SALES_PER_BED'].describe())

# Save analysis results
df.to_csv('cortho_analyzed.csv', index=False)

# 8. Visualizations
plt.figure(figsize=(10, 6))
sns.histplot(df['SALESY'], bins=50, kde=True)
plt.title('Distribution of SALESY')
plt.savefig('salesy_dist.png')
plt.close()

plt.figure(figsize=(12, 8))
top_corrs = corrs.drop('SALESY').head(10)
sns.barplot(x=top_corrs.values, y=top_corrs.index)
plt.title('Top 10 Correlations with SALESY')
plt.savefig('correlations.png')
plt.close()

plt.figure(figsize=(10, 6))
sns.boxplot(x='TH', y='SALESY', data=df)
plt.title('SALESY by Teaching Hospital (TH)')
plt.savefig('salesy_by_th.png')
plt.close()

plt.figure(figsize=(10, 6))
sns.scatterplot(x='TOTAL_OPS', y='SALESY', hue='TRAUMA', data=df, alpha=0.5)
plt.title('Total Operations vs SALESY (colored by Trauma Unit)')
plt.savefig('ops_vs_sales.png')
plt.close()

print("\nVisualizations saved to .png files.")
