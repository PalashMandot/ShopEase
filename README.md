# ShopEase - Modern E-Commerce Web Portal
### Academic Project for 3rd Year CSE (TA-2 Evaluation)

---

## 1. Project Overview
**ShopEase** is a full-stack, responsive e-commerce web portal built for modern online shopping. It provides a complete end-to-end purchasing workflow from registration and product browsing to shopping cart management, Cash on Delivery (COD) checkout, order history tracking, and an administrative control panel for inventory and fulfillment.

Designed specifically for 3rd-year Computer Science & Engineering students, the codebase follows clean software design principles with zero boilerplate clutter, parameterized SQL queries for security, and intuitive Jinja2 template inheritance.

---

## 2. Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend** | HTML5, Vanilla CSS3, JavaScript (ES6) | Responsive grid, Google Font *Plus Jakarta Sans*, modern card UI, micro-animations, no bloated CSS framework dependencies. |
| **Backend** | Python 3.12, Flask 3.1 | Lightweight, high-performance WSGI web application framework. |
| **Database** | SQLite 3 | Embedded relational database with Foreign Key constraints and parameterized queries. |
| **Security** | Werkzeug Security | Industry-standard PBKDF2/SHA256 password hashing and role-based access control (RBAC). |

---

## 3. Architecture & Project Structure

```
ShopEase/
├── app.py                     # Main Flask Application (Routes, Session & Auth logic)
├── database.py                # Database helpers, connection pooling & schema DDL
├── init_db.py                 # Standalone DB initialization & seed data script
├── test_portal.py             # Automated unit & integration test suite (10/10 test cases)
├── requirements.txt           # Project dependencies
├── README.md                  # Complete academic guide & documentation
├── TEST_REPORT.md             # Test cases, expected results & screenshot guide
│
├── static/
│   ├── css/
│   │   └── style.css          # Design system, responsive layout & custom components
│   └── js/
│       └── main.js            # Toast alerts, quantity selectors & AJAX cart actions
│
└── templates/
    ├── base.html              # Base layout with navbar, search, alerts & footer
    ├── index.html             # Home page (hero banner, categories, featured items)
    ├── products.html          # Product catalog (search, filter & sort)
    ├── product_detail.html    # Detailed product view with stock badges
    ├── cart.html              # Shopping cart with quantity updates & summary
    ├── checkout.html          # Checkout form with COD payment selection
    ├── order_success.html     # Order confirmation with Order ID & delivery estimate
    ├── orders.html            # Customer order history table
    ├── order_detail.html      # Individual order receipt & tracking timeline
    ├── profile.html           # Customer profile & account metrics
    ├── auth/
    │   ├── login.html         # Login page with 1-click demo credential autofill
    │   └── register.html      # Customer registration with server-side validation
    └── admin/
        ├── dashboard.html     # Admin analytics dashboard (KPIs, revenue, alerts)
        ├── products.html      # Inventory management & stock updates
        ├── product_form.html  # Add/Edit product form
        ├── categories.html    # Category creation & management
        └── orders.html        # Order fulfillment status manager
```

---

## 4. Database Schema (SQLite)

The database `shopease.db` contains 6 relational tables designed with 3NF normalization:

```
+--------------------+        +---------------------+
|     categories     |        |        users        |
+--------------------+        +---------------------+
| id (PK)            |        | id (PK)             |
| name (UNIQUE)      |        | name                |
| description        |        | email (UNIQUE)      |
| icon               |        | password_hash       |
| created_at         |        | phone, address      |
+---------+----------+        | is_admin (0 or 1)   |
          |                   | created_at          |
          | 1:N               +----------+----------+
          v                              | 1:N
+--------------------+                   |
|      products      |                   |
+--------------------+                   |
| id (PK)            |                   |
| category_id (FK)   |                   |
| name, description  |                   v
| price, stock       |        +---------------------+
| image_url          |        |     cart_items      |
| featured           |        +---------------------+
| created_at         |        | id (PK)             |
+---------+----------+        | user_id (FK)        |
          |                   | product_id (FK)     |
          | 1:N               | quantity            |
          |                   +---------------------+
          v                              |
+--------------------+                   |
|    order_items     |                   v
+--------------------+        +---------------------+
| id (PK)            |        |       orders        |
| order_id (FK)      |<-------| id (PK)             |
| product_id (FK)    |  1:N   | order_number (UNQ)  |
| product_name       |        | user_id (FK)        |
| product_image      |        | customer_name       |
| price (SNAPSHOT!)  |        | customer_email      |
| quantity, subtotal |        | shipping_address    |
+--------------------+        | payment_method (COD)|
                              | subtotal, total     |
                              | status (Pending...) |
                              +---------------------+
```

> **Design Highlight for Evaluators:**
> In `order_items`, the product name, image, and price are **snapshotted at the exact moment of purchase**. This ensures historical order totals and invoices remain 100% accurate even if an admin subsequently edits product details or changes prices.

---

## 5. Setup & Running Instructions

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- `pip` (Python package manager)

### Step 1: Clone or Navigate to the Project Directory
```bash
cd ShopEase
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database & Seed Sample Records
```bash
python init_db.py
```
*This command creates `shopease.db`, tables, and populates 14+ products across 5 categories with high-quality images and descriptions.*

### Step 4: Run the Application
```bash
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 6. Default Demo Credentials

For quick evaluation and testing, the application comes with ready-to-use accounts (and 1-click autofill buttons on the login screen):

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Administrator** | `admin@shopease.com` | `admin123` | Full access to `/admin`, KPI dashboard, product CRUD, stock manager, and order status updater |
| **Customer** | `user@shopease.com` | `user123` | Standard customer access, shopping cart, checkout, profile, and order history |

---

## 7. Running the Automated Test Suite

A comprehensive test suite covering all 10 evaluation requirements is included:
```bash
python test_portal.py
```

Expected Output:
```
.........
----------------------------------------------------------------------
Ran 9 tests in 1.249s

OK
[PASS] Step 1: Customer registered successfully.
[PASS] Step 2: Customer logged in successfully.
[PASS] Step 3: Browse and search products functional.
[PASS] Step 4: Product added to cart successfully.
[PASS] Step 5: Cart quantity updated successfully.
[PASS] Steps 6 & 7: Checkout placed order, stock decremented, and visible in order history.
[PASS] Step 8: Admin authenticated and dashboard rendered.
[PASS] Step 9: Admin added product and updated inventory stock.
[PASS] Step 10: Admin updated order status from Pending to Shipped.
```

---

## 8. Modules Breakdown & Features

### Module 1: User Authentication & Security
- Secure registration with validation for email uniqueness, password confirmation, and length.
- Password hashing using `werkzeug.security.generate_password_hash` (PBKDF2-HMAC-SHA256).
- Session-based authentication with `session['user_id']`, `session['user_name']`, and `session['is_admin']`.
- Custom decorators `@login_required` and `@admin_required` protecting sensitive routes.

### Module 2: Product Catalog & Exploration
- Multi-category navigation bar and category pills.
- Real-time keyword search against both product name and product description.
- Multi-criteria sorting: Price (Low to High, High to Low), Alphabetical (A-Z), and Newest Arrivals.
- Product detail page showing live stock badges ("In Stock", "Low Stock", "Out of Stock"), high-res imagery, and related recommendations.

### Module 3: Dynamic Shopping Cart
- Hybrid cart architecture: supports guest session cart and automatic migration to database-backed cart upon user login.
- Dynamic navbar badge showing real-time item count.
- Quantity modification with upper bounds capped by actual warehouse stock.
- Instant item removal and clear cart options.

### Module 4: Checkout & Order Processing
- Server-side stock verification right before order commit to prevent race conditions or overselling.
- Free delivery calculation (Free shipping above ₹999, else flat ₹99).
- Automatic generation of unique alphanumeric order numbers (e.g. `SE-20261028-XXXX`).
- Cash on Delivery (COD) payment method with clear verification notice.
- Real-time stock decrement upon successful order placement.

### Module 5: Admin Control Center
- Analytics Dashboard: Total Sales Revenue, Total Orders, Total Products, Customer Count, Low Stock Watchlist.
- Product Management: Add new products with image preview, edit attributes, inline stock updates, and safe deletion.
- Category Management: Create new categories with customizable icons and deletion safeguard preventing deletion if products are linked.
- Order Fulfillment: Review customer details and update order status through 5 phases: *Pending &rarr; Processing &rarr; Shipped &rarr; Delivered &rarr; Cancelled*.

---

## 9. Viva / Defense Preparation Guide (Frequently Asked Questions)

### Q1: Why did you choose SQLite over MySQL or PostgreSQL for this project?
> **Answer:** SQLite is a serverless, zero-configuration relational database stored directly in a file (`shopease.db`). It enforces ACID compliance, supports full SQL syntax, foreign keys, and indexes, making it ideal for self-contained academic projects without requiring external database server installations.

### Q2: How do you prevent SQL Injection attacks?
> **Answer:** All database operations in `database.py` and `app.py` use **parameterized queries** with `?` placeholders (e.g., `cur.execute("SELECT * FROM users WHERE email = ?", (email,))`). User input is never concatenated directly into SQL strings, completely preventing SQL injection.

### Q3: How is password security handled?
> **Answer:** Passwords are never stored in plain text. We utilize Werkzeug's `generate_password_hash()` which generates a salted PBKDF2 hash with SHA-256 encryption. During login, `check_password_hash()` safely verifies the hash against the entered password in constant time to prevent timing attacks.

### Q4: What happens if two users try to buy the last remaining item in stock?
> **Answer:** The `/checkout/place-order` route performs server-side stock verification inside a database transaction before committing the order. If the requested quantity exceeds the current stock, the transaction is rejected with an informative error message, preventing negative stock or overselling.

### Q5: How does the application distinguish regular users from administrators?
> **Answer:** The `users` table has an integer column `is_admin` (1 for admin, 0 for customer). The `@admin_required` decorator checks `session.get('is_admin') == 1`. If an unprivileged user tries to access `/admin`, they are redirected and a warning flash is displayed.
