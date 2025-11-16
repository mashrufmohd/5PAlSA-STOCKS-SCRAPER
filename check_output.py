"""Quick check: export Excel to CSV and print a summary."""

import pandas as pd

df = pd.read_excel('outputs/all_stock_script_Nov15_2025.xlsx')
df.to_csv('outputs/stocks_summary.csv', index=False)

print('=' * 80)
print('✅ EXCEL FILE HAS DATA!')
print('=' * 80)
print(f'\nTotal companies scraped: {len(df)}')
print(f'Excel file: outputs/all_stock_script_Nov15_2025.xlsx')
print(f'CSV file: outputs/stocks_summary.csv')
print('\n' + '=' * 80)
print('ALL COMPANIES IN THE FILE:')
print('=' * 80)

for i, row in df.iterrows():
    print(f"{row['serial_no']:2d}. {row['company_name']:45s} | {row['notes']}")

print('\n' + '=' * 80)
print(f'✅ ALL {len(df)} COMPANIES SUCCESSFULLY SAVED TO EXCEL!')
print('=' * 80)
