"""
init_db.py - Standalone database initializer for ShopEase.
Run this script to initialize tables and populate sample products, categories, and test accounts.
Usage:
    python init_db.py
"""

from database import init_db, seed_data

if __name__ == '__main__':
    print("Initializing ShopEase SQLite database...")
    init_db()
    print("Database tables created successfully.")
    print("Seeding sample categories, products, and default accounts...")
    seed_data()
    print("Database initialization complete!")
    print("\nDefault Accounts:")
    print("  Administrator: admin@shopease.com / admin123")
    print("  Customer:      user@shopease.com  / user123")
