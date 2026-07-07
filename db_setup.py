import db_adapter

print("Initializing POS database...")
try:
    db_adapter.init_tables()
    print("Database and tables verified/created successfully!")
    print("Seeded Default Employees:")
    print("  - Manager: dxd (password: ryomen)")
    print("  - Cashiers: rocky2003, rohith_2k3, aniruths003, giffyy")
except Exception as e:
    print(f"Error during database initialization: {e}")
