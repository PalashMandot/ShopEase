"""
database.py - Database operations and connection management for ShopEase.
Uses Python's built-in sqlite3 library with parameterized queries for security.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'shopease.db')


def get_db():
    """
    Establishes connection to the SQLite database.
    Configures row_factory to sqlite3.Row for convenient dict-like column access.
    Enables foreign key enforcement.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def query_db(query, args=(), one=False):
    """
    Executes a SELECT query using parameterized statements to prevent SQL Injection.
    Returns a single row or list of rows.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query, args=(), commit=True):
    """
    Executes an INSERT, UPDATE, or DELETE query.
    Returns the lastrowid of an inserted row or rowcount.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    last_id = cur.lastrowid
    if commit:
        conn.commit()
    cur.close()
    conn.close()
    return last_id


def init_db():
    """
    Creates all necessary database tables for the ShopEase portal:
    - users: stores customers and administrators
    - categories: product classifications
    - products: inventory items with price and stock
    - cart_items: active user shopping carts
    - orders: finalized purchases with customer delivery details
    - order_items: line items snapshotting purchase prices
    """
    conn = get_db()
    cur = conn.cursor()

    # Users Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        is_admin INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Categories Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        icon TEXT DEFAULT 'bi-tag',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Products Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL CHECK(price >= 0),
        stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
        image_url TEXT NOT NULL,
        featured INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT
    );
    ''')

    # Shopping Cart Items Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
        UNIQUE(user_id, product_id)
    );
    ''')

    # Orders Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL UNIQUE,
        user_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        shipping_address TEXT NOT NULL,
        city TEXT NOT NULL,
        postal_code TEXT NOT NULL,
        order_notes TEXT,
        payment_method TEXT NOT NULL DEFAULT 'Cash on Delivery',
        subtotal REAL NOT NULL,
        shipping_fee REAL NOT NULL DEFAULT 0.0,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT
    );
    ''')

    # Order Items Table (Snapshots product info and price at purchase time)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER,
        product_name TEXT NOT NULL,
        product_image TEXT,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE SET NULL
    );
    ''')

    conn.commit()
    conn.close()


def seed_data():
    """
    Populates sample data for immediate testing and academic demonstration:
    - Default Admin account
    - Default Customer account
    - Curated Categories (Electronics, Fashion, Home & Kitchen, Books, Fitness)
    - 12+ Sample Products with images, prices, stock, and descriptions
    """
    init_db()
    conn = get_db()
    cur = conn.cursor()

    # 1. Seed Users (if not existing)
    admin_exists = cur.execute("SELECT id FROM users WHERE email = 'admin@shopease.com'").fetchone()
    if not admin_exists:
        cur.execute('''
            INSERT INTO users (name, email, password_hash, phone, address, is_admin)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (
            'Administrator',
            'admin@shopease.com',
            generate_password_hash('admin123'),
            '+91 9876543210',
            'ShopEase HQ, Bengaluru, India'
        ))

    customer_exists = cur.execute("SELECT id FROM users WHERE email = 'user@shopease.com'").fetchone()
    if not customer_exists:
        cur.execute('''
            INSERT INTO users (name, email, password_hash, phone, address, is_admin)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (
            'Rahul Sharma',
            'user@shopease.com',
            generate_password_hash('user123'),
            '+91 9876543211',
            'Flat 402, Green Glen Layout, Bellandur, Bengaluru'
        ))

    # 2. Seed Categories
    categories = [
        ('Electronics', 'Latest gadgets, accessories, audio, and personal computing.', 'bi-laptop'),
        ('Fashion', 'Trendy clothing, stylish footwear, and designer accessories.', 'bi-bag-check'),
        ('Home & Kitchen', 'Modern home essentials, smart kitchen appliances, and decor.', 'bi-house-door'),
        ('Books & Stationery', 'Bestselling novels, educational materials, and premium stationery.', 'bi-book'),
        ('Sports & Fitness', 'High-performance gym gear, athletic wear, and fitness accessories.', 'bi-heart-pulse')
    ]

    for name, desc, icon in categories:
        cur.execute('''
            INSERT OR IGNORE INTO categories (name, description, icon)
            VALUES (?, ?, ?)
        ''', (name, desc, icon))

    conn.commit()

    # Map category names to IDs
    cur.execute("SELECT id, name FROM categories")
    cat_map = {row['name']: row['id'] for row in cur.fetchall()}

    # 3. Seed Products (if table is empty or has fewer than 10 products)
    product_count = cur.execute("SELECT COUNT(*) as count FROM products").fetchone()['count']
    if product_count < 5:
        sample_products = [
            # Electronics
            (
                cat_map['Electronics'],
                'Noise-Cancelling Wireless Headphones',
                'Premium over-ear Bluetooth headphones featuring active noise cancellation, 40-hour battery life, and crystal-clear bass.',
                4999.00,
                35,
                'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80',
                1
            ),
            (
                cat_map['Electronics'],
                'Ultra HD Smart Watch Pro',
                'Advanced fitness smartwatch with continuous heart rate monitoring, SpO2 sensor, AMOLED touchscreen, and IP68 waterproof rating.',
                2799.00,
                50,
                'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80',
                1
            ),
            (
                cat_map['Electronics'],
                'Mechanical RGB Gaming Keyboard',
                'Compact tenkeyless mechanical keyboard with tactile blue switches, customizable RGB backlighting, and durable aluminium body.',
                3299.00,
                25,
                'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80',
                0
            ),
            (
                cat_map['Electronics'],
                'Portable Bluetooth Waterproof Speaker',
                'Compact outdoor speaker with 360-degree stereo sound, 12 hours playtime, and IPX7 rugged waterproof construction.',
                1899.00,
                40,
                'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&auto=format&fit=crop&q=80',
                0
            ),

            # Fashion
            (
                cat_map['Fashion'],
                'Classic Oxford Cotton Shirt',
                '100% breathable organic cotton slim-fit button-down shirt. Perfect for both formal business wear and weekend casuals.',
                1299.00,
                60,
                'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80',
                1
            ),
            (
                cat_map['Fashion'],
                'Urban Minimalist Backpack',
                'Sleek water-repellent city backpack with a padded 15.6-inch laptop compartment, hidden anti-theft pocket, and USB charging pass.',
                1699.00,
                30,
                'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=80',
                1
            ),
            (
                cat_map['Fashion'],
                'Lightweight Running Sneakers',
                'Ultra-breathable knit athletic sneakers with responsive cushioned midsole designed for daily jogging and gym workouts.',
                2499.00,
                45,
                'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80',
                1
            ),

            # Home & Kitchen
            (
                cat_map['Home & Kitchen'],
                'Stainless Steel Pour-Over Coffee Maker',
                'Double-wall insulated pour-over coffee brewer with permanent micro-mesh stainless steel filter for barista-level artisan coffee.',
                1499.00,
                20,
                'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=80',
                0
            ),
            (
                cat_map['Home & Kitchen'],
                'Smart LED Ambient Desk Lamp',
                'Modern dimmable desk lamp with wireless smartphone charging base, color temperature adjustment, and touch control sensor.',
                2199.00,
                28,
                'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop&q=80',
                0
            ),
            (
                cat_map['Home & Kitchen'],
                'Ceramic Non-Stick Cookware Pan',
                'Eco-friendly non-toxic granite coating frying pan with heat-resistant ergonomic wooden handle. Induction base compatible.',
                1350.00,
                18,
                'https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop&q=80',
                0
            ),

            # Books & Stationery
            (
                cat_map['Books & Stationery'],
                'Designing Data-Intensive Applications',
                'The definitive guide to the concepts and architectures of reliable, scalable, and maintainable data systems by Martin Kleppmann.',
                1850.00,
                22,
                'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80',
                1
            ),
            (
                cat_map['Books & Stationery'],
                'Handcrafted Leather Journal Notebook',
                'Rustic genuine leather bound notebook with 240 blank unlined deckle edge antique paper pages, ideal for journaling and sketching.',
                899.00,
                55,
                'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=600&auto=format&fit=crop&q=80',
                0
            ),

            # Sports & Fitness
            (
                cat_map['Sports & Fitness'],
                'Premium Non-Slip Yoga Mat',
                'Extra-thick 6mm eco-friendly TPE alignment yoga mat with dual-side textured non-slip grip and carrying strap included.',
                1199.00,
                38,
                'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&auto=format&fit=crop&q=80',
                1
            ),
            (
                cat_map['Sports & Fitness'],
                'Adjustable Dumbbells Set (20 kg)',
                'Heavy-duty cast iron adjustable dumbbell pair with connecting bar to convert into barbell for comprehensive home strength training.',
                3899.00,
                15,
                'https://images.unsplash.com/photo-1586401100295-7a8096fd231a?w=600&auto=format&fit=crop&q=80',
                0
            )
        ]

        cur.executemany('''
            INSERT INTO products (category_id, name, description, price, stock, image_url, featured)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_products)

        conn.commit()

    conn.close()
