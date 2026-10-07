from app.data_loader import load_sales_data, load_targets_data


sales = load_sales_data()
targets = load_targets_data()

print("\n===== SALES DATA =====")
print(sales)

print("\n===== SALES COLUMNS =====")
print(sales.columns.tolist())

print("\n===== TARGET DATA =====")
print(targets)

print("\n===== TARGET COLUMNS =====")
print(targets.columns.tolist())