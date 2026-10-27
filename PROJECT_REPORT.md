# ACADEMIC PROJECT REPORT

## **ShopEase — Modern Full-Stack E-Commerce Web Portal**

---

### **Project Metadata**
- **Course / Assessment:** Technical Assessment 2 (TA-2) / Capstone Mini-Project
- **Department:** Department of Computer Science & Engineering
- **Student Name:** Palash Mandot
- **Email:** palashmandot7@gmail.com
- **GitHub Repository:** [https://github.com/PalashMandot/ShopEase](https://github.com/PalashMandot/ShopEase)
- **Academic Year:** 3rd Year CSE (2026)
- **Technology Stack:** Python 3.12, Flask 3.1, SQLite 3, HTML5, Vanilla CSS3, JavaScript (ES6)

---

# TABLE OF CONTENTS
1. [Abstract](#1-abstract)
2. [Introduction & Problem Statement](#2-introduction--problem-statement)
3. [Objectives & Project Scope](#3-objectives--project-scope)
4. [Software Requirements Specification (SRS)](#4-software-requirements-specification-srs)
   - 4.1 Functional Requirements
   - 4.2 Non-Functional Requirements
   - 4.3 Hardware & Software Specifications
5. [System Architecture & Design](#5-system-architecture--design)
   - 5.1 Architectural Pattern (Model-Template-View)
   - 5.2 Entity-Relationship (ER) Diagram
   - 5.3 Relational Database Schema Specifications
   - 5.4 Data Flow Diagrams (DFD Level 0 and Level 1)
6. [Detailed Module Design & Implementation](#6-detailed-module-design--implementation)
   - 6.1 Module 1: User Authentication & Role-Based Access Control
   - 6.2 Module 2: Dynamic Product Catalog & Search/Filter Engine
   - 6.3 Module 3: Persistent & Session-Based Shopping Cart
   - 6.4 Module 4: Secure Checkout, Order Processing & Inventory Reduction
   - 6.5 Module 5: Administrative Control Center & Analytics Dashboard
7. [Security Analysis & Design Decisions](#7-security-analysis--design-decisions)
8. [Testing & Quality Assurance](#8-testing--quality-assurance)
   - 8.1 Testing Methodology
   - 8.2 Test Suite Execution Matrix (10 Core Cases)
   - 8.3 Verification Results
9. [User Interface Design & Screenshots Guide](#9-user-interface-design--screenshots-guide)
10. [Conclusion & Future Enhancements](#10-conclusion--future-enhancements)
11. [References & Bibliography](#11-references--bibliography)
12. [Appendix: College Evaluation Viva Q&A Guide](#12-appendix-college-evaluation-viva-qa-guide)

---

# 1. Abstract

Modern digital commerce demands intuitive user interfaces, real-time catalog navigation, resilient state management, and strict backend data integrity. **ShopEase** is a production-grade full-stack electronic commerce portal developed to satisfy the comprehensive criteria of a 3rd-year Computer Science & Engineering capstone project (TA-2).

The portal is implemented using a decoupled yet lightweight architectural paradigm: **Python Flask** handles routing, server-side data validation, business logic, and session security; **SQLite 3** provides an embedded ACID-compliant relational persistence store; and **HTML5, Vanilla CSS3, and ES6 JavaScript** power a responsive, modern presentation layer with zero heavyweight framework overhead. 

The application satisfies five mandatory operational modules: User Authentication with cryptographic password hashing (PBKDF2-HMAC-SHA256); Catalog Discovery with multi-criteria search, category filtering, and price sorting; a resilient Shopping Cart supporting session-to-database cart migration; a server-validated Checkout process utilizing Cash on Delivery (COD) with purchase-time price snapshotting and atomic inventory decrements; and a secure Administrative Control Center providing Key Performance Indicator (KPI) analytics, stock management, and fulfillment pipeline status updates. Complete unit and integration testing verified all 10 core evaluation workflows with a 100% pass rate.

---

# 2. Introduction & Problem Statement

### 2.1 Background
Electronic commerce platforms serve as critical infrastructure in modern computing, exemplifying key computer science concepts including client-server networking, stateful HTTP session management, relational database normalization, transaction processing, and access control.

### 2.2 Problem Statement
Many introductory educational web projects suffer from architectural shortcomings:
1. **Security Vulnerabilities:** Storing plaintext passwords, exposing SQL injection flaws through string formatting, or trusting client-side price values during checkout.
2. **Data Anomalies & Historical Inconsistency:** Referencing live product records directly from past orders, causing historic order summaries to alter if product prices or titles change later in the catalog.
3. **Concurrency & Inventory Overselling:** Failing to re-validate inventory levels at the exact moment of order commitment.
4. **Poor Usability & Over-Engineered Dependencies:** Relying on bloated client frameworks that make code difficult to explain and defend during university technical viva evaluations.

### 2.3 Proposed Solution: ShopEase
ShopEase directly addresses these challenges by implementing:
- Server-side cryptographic password hashing using industry-standard libraries.
- Parameterized SQL execution preventing SQL Injection.
- Historical price snapshotting in the `order_items` relation.
- Server-side inventory boundaries preventing race conditions and negative inventory.
- Clean, self-documenting Python and Vanilla web code designed for academic defense.

---

# 3. Objectives & Project Scope

### 3.1 Primary Objectives
- Design and construct an end-to-end e-commerce web portal with clean separation between database queries, application routing, and user interface templates.
- Implement robust role-based authentication separating regular customers from site administrators.
- Deliver an interactive storefront with keyword search, category navigation, dynamic sorting, and stock status indicators.
- Create an intuitive shopping cart and checkout pipeline supporting Cash on Delivery without requiring third-party payment gateways.
- Provide administrators with a dashboard displaying real-time financial and operational metrics (revenue, orders, product counts, stock alerts).

### 3.2 Scope of the System
- **In Scope:** Customer account registration, login/logout, session management, product discovery, catalog filtering, cart quantity controls, order placement, purchase history tracking, order detail invoice generation, admin product CRUD, inline stock restocking, category management, and order status transitions (*Pending &rarr; Processing &rarr; Shipped &rarr; Delivered &rarr; Cancelled*).
- **Out of Scope (By Project Specification):** External third-party payment gateways (Razorpay, Stripe), physical shipment API tracking integrations, multi-vendor marketplaces.

---

# 4. Software Requirements Specification (SRS)

### 4.1 Functional Requirements

| Module | Requirement ID | Requirement Description |
|---|---|---|
| **Module 1: Authentication** | FR-1.1 | The system shall allow new customers to register by providing name, unique email, password, phone, and address. |
| | FR-1.2 | The system shall hash user passwords using PBKDF2-HMAC-SHA256 prior to database insertion. |
| | FR-1.3 | The system shall authenticate returning users and store role credentials in encrypted server-side session cookies. |
| | FR-1.4 | The system shall provide secure logout terminating user sessions. |
| **Module 2: Catalog** | FR-2.1 | The system shall display inventory products with image, title, price, category, and stock indicators. |
| | FR-2.2 | The system shall support keyword search matching both product titles and descriptions. |
| | FR-2.3 | The system shall enable category filtering and sorting (Price Low-to-High, High-to-Low, Newest). |
| | FR-2.4 | The system shall provide individual product detail views with related item suggestions. |
| **Module 3: Shopping Cart** | FR-3.1 | The system shall allow users to add items to the cart and specify quantities up to available stock. |
| | FR-3.2 | The system shall allow quantity incrementation, decrementation, and individual item deletion. |
| | FR-3.3 | The system shall compute real-time line subtotals, order subtotal, shipping fee, and grand total. |
| | FR-3.4 | The system shall migrate guest session carts into the database upon user authentication. |
| **Module 4: Checkout & Orders** | FR-4.1 | The system shall validate delivery address, postal code, and contact information before order placement. |
| | FR-4.2 | The system shall re-verify product availability on the server to prevent overselling. |
| | FR-4.3 | The system shall generate a unique alphanumeric order identifier (e.g. `SE-20261028-XXXX`). |
| | FR-4.4 | The system shall snapshot unit prices into `order_items` and deduct warehouse inventory. |
| | FR-4.5 | The system shall present an order confirmation screen and persist records in customer order history. |
| **Module 5: Admin Dashboard** | FR-5.1 | The system shall restrict administrative routes to users with `is_admin = 1`. |
| | FR-5.2 | The system shall display aggregated KPIs: Total Sales, Total Orders, Products, and Low Stock Alerts. |
| | FR-5.3 | The system shall allow administrators to create, edit, restock, and delete product inventory. |
| | FR-5.4 | The system shall allow administrators to transition order fulfillment statuses. |

### 4.2 Non-Functional Requirements
- **Security:** Parameterized database queries to prevent SQL Injection; HTTP session cookies signed with application secret key; server-side sanitization of all inputs.
- **Performance:** Sub-100ms response times for catalog queries through indexed primary and foreign keys in SQLite.
- **Reliability & ACID Compliance:** Relational transactions ensure orders, line items, and stock deductions succeed or rollback together atomically.
- **Usability & Responsiveness:** Clean modern typography (*Plus Jakarta Sans*), fluid CSS Grid and Flexbox layouts adapting across desktop, tablet, and mobile displays.

### 4.3 Hardware & Software Specifications
- **Client Machine:** Modern web browser (Chrome, Edge, Firefox, Safari)
- **Host Machine:** Minimum 1 GHz processor, 1 GB RAM, 200 MB free disk space
- **Operating System:** Platform independent (Windows 10/11, macOS, Linux)
- **Runtime Environment:** Python 3.10+ (tested on Python 3.12.9)
- **Key Dependencies:** Flask >= 3.0.0, Werkzeug >= 3.0.0

---

# 5. System Architecture & Design

### 5.1 Architectural Pattern
ShopEase adopts the **Model-Template-View (MTV)** pattern:
- **Model:** SQLite database handled via `database.py` with relational schema definitions, constraints, and connection pooling.
- **Template:** Presentation layer rendered using Jinja2 templates (`base.html`, storefront, cart, checkout, admin).
- **View / Controller:** Flask application routing layer (`app.py`) handling HTTP requests, decorators, validation, and session orchestration.

```
+-------------------------------------------------------------------------+
|                              CLIENT BROWSER                             |
|               (HTML5, Vanilla CSS3, JavaScript ES6 Fetch)               |
+------------------------------------+------------------------------------+
                                     | HTTP Requests (GET / POST)
                                     v
+-------------------------------------------------------------------------+
|                             FLASK WEB SERVER                            |
|  +-------------------------------------------------------------------+  |
|  | Context Processors (Cart Badge Count, Categories, Auth User)      |  |
|  +-------------------------------------------------------------------+  |
|  | Route Handlers & Controllers (app.py)                             |  |
|  |   - Auth Controller (/register, /login, /logout)                  |  |
|  |   - Catalog Controller (/, /products, /product/<id>)              |  |
|  |   - Cart Controller (/cart, /cart/add, /cart/update, /cart/remove)|  |
|  |   - Checkout Controller (/checkout, /checkout/place-order)        |  |
|  |   - Admin Controller (/admin, /admin/products, /admin/orders)     |  |
|  +-------------------------------------------------------------------+  |
|  | Access Control Decorators (@login_required, @admin_required)      |  |
|  +-------------------------------------------------------------------+  |
|  | Database Abstraction & Helper Layer (database.py)                 |  |
+------------------------------------+------------------------------------+
                                     | Parameterized SQL Queries (?)
                                     v
+-------------------------------------------------------------------------+
|                         SQLITE 3 RELATIONAL DB                          |
|             (users, categories, products, cart_items, orders,           |
|                              order_items)                               |
+-------------------------------------------------------------------------+
```

### 5.2 Entity-Relationship (ER) Diagram

```
+------------------+         +-------------------+
|    CATEGORIES    |         |       USERS       |
+------------------+         +-------------------+
| *id (PK)         |         | *id (PK)          |
|  name (UNIQUE)   |         |  name             |
|  description     |         |  email (UNIQUE)   |
|  icon            |         |  password_hash    |
|  created_at      |         |  phone, address   |
+--------+---------+         |  is_admin         |
         |                   |  created_at       |
         | 1                 +----+---------+----+
         |                        | 1       | 1
         | N                      |         |
         v                        | N       | N
+------------------+              |         |
|     PRODUCTS     |              |         |
+------------------+              |         |
| *id (PK)         |              |         |
|  category_id(FK) |              |         |
|  name            |              v         v
|  description     |      +---------------+ +------------------+
|  price           |      |  CART_ITEMS   | |      ORDERS      |
|  stock           |      +---------------+ +------------------+
|  image_url       |      | *id (PK)      | | *id (PK)         |
|  featured        |      |  user_id (FK) | |  order_number    |
|  created_at      |      |  product_id(FK| |  user_id (FK)    |
+--------+---------+      |  quantity     | |  customer_name   |
         | 1              |  created_at   | |  customer_email  |
         |                +---------------+ |  customer_phone  |
         | N                                |  shipping_address|
         v                                  |  city, postal_code
+------------------+                        |  payment_method  |
|   ORDER_ITEMS    |                        |  subtotal, fee   |
+------------------+                        |  total_amount    |
| *id (PK)         |                        |  status          |
|  order_id (FK)   |<-----------------------|  created_at      |
|  product_id (FK) |           1            +------------------+
|  product_name    |
|  product_image   |
|  price (SNAPSHOT)|
|  quantity        |
|  subtotal        |
+------------------+
```

### 5.3 Relational Database Schema Specifications

#### 1. `users` Table
Stores customer and administrator profiles.
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `name` TEXT NOT NULL
- `email` TEXT NOT NULL UNIQUE
- `password_hash` TEXT NOT NULL
- `phone` TEXT
- `address` TEXT
- `is_admin` INTEGER NOT NULL DEFAULT 0 *(0 = Customer, 1 = Administrator)*
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### 2. `categories` Table
Organizes products into classification tiers.
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `name` TEXT NOT NULL UNIQUE
- `description` TEXT
- `icon` TEXT DEFAULT 'bi-tag'
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### 3. `products` Table
Inventory items available for purchase.
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `category_id` INTEGER NOT NULL, FOREIGN KEY REFERENCES `categories(id)` ON DELETE RESTRICT
- `name` TEXT NOT NULL
- `description` TEXT NOT NULL
- `price` REAL NOT NULL CHECK(price >= 0)
- `stock` INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0)
- `image_url` TEXT NOT NULL
- `featured` INTEGER DEFAULT 0
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### 4. `cart_items` Table
Persistent user cart selections before order placement.
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `user_id` INTEGER NOT NULL, FOREIGN KEY REFERENCES `users(id)` ON DELETE CASCADE
- `product_id` INTEGER NOT NULL, FOREIGN KEY REFERENCES `products(id)` ON DELETE CASCADE
- `quantity` INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0)
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- CONSTRAINT: `UNIQUE(user_id, product_id)`

#### 5. `orders` Table
Master record of finalized purchases.
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `order_number` TEXT NOT NULL UNIQUE
- `user_id` INTEGER NOT NULL, FOREIGN KEY REFERENCES `users(id)` ON DELETE RESTRICT
- `customer_name` TEXT NOT NULL
- `customer_email` TEXT NOT NULL
- `customer_phone` TEXT NOT NULL
- `shipping_address` TEXT NOT NULL
- `city` TEXT NOT NULL
- `postal_code` TEXT NOT NULL
- `order_notes` TEXT
- `payment_method` TEXT NOT NULL DEFAULT 'Cash on Delivery'
- `subtotal` REAL NOT NULL
- `shipping_fee` REAL NOT NULL DEFAULT 0.0
- `total_amount` REAL NOT NULL
- `status` TEXT NOT NULL DEFAULT 'Pending' *(Values: Pending, Processing, Shipped, Delivered, Cancelled)*
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

#### 6. `order_items` Table
Line-item details preserving purchase-time product attributes.
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `order_id` INTEGER NOT NULL, FOREIGN KEY REFERENCES `orders(id)` ON DELETE CASCADE
- `product_id` INTEGER, FOREIGN KEY REFERENCES `products(id)` ON DELETE SET NULL
- `product_name` TEXT NOT NULL *(Snapshotted)*
- `product_image` TEXT *(Snapshotted)*
- `price` REAL NOT NULL *(Snapshotted purchase unit price)*
- `quantity` INTEGER NOT NULL
- `subtotal` REAL NOT NULL

---

# 6. Detailed Module Design & Implementation

### 6.1 Module 1: User Authentication & Role-Based Access Control
- **Registration (`/register`):** Collects user information, verifies email uniqueness, and verifies matching password confirmation. Passwords are encrypted using Werkzeug's `generate_password_hash()`.
- **Login (`/login`):** Validates credentials using `check_password_hash()`. On success, sets `session['user_id']`, `session['user_name']`, `session['user_email']`, and `session['is_admin']`.
- **Guest-to-User Cart Migration:** If a visitor added items to their shopping cart before logging in, `merge_guest_cart_to_db()` automatically reads their guest session cart, checks warehouse stock, and inserts/merges those items into the user's permanent SQLite cart table.
- **Access Control Decorators:**
  - `@login_required`: Redirects unauthenticated visitors to `/login?next=<target_url>`.
  - `@admin_required`: Restricts endpoints strictly to sessions with `is_admin == 1`. Unauthorized requests are redirected to home with a danger alert.

### 6.2 Module 2: Dynamic Product Catalog & Search/Filter Engine
- **Search System:** Implemented via parameterized SQL queries checking wildcard terms across both name and description: `WHERE p.name LIKE ? OR p.description LIKE ?`.
- **Categorization:** Dynamic category pills filter results by `category_id`.
- **Multi-Factor Sorting:** Allows users to order items by Price (Ascending/Descending), Name (A-Z), and Newest arrivals.
- **Stock Awareness:** Displays contextual badges: *In Stock (X units)*, *Low Stock (Only X left)* when stock is under 10, and *Out of Stock* with add-to-cart buttons disabled when stock is zero.

### 6.3 Module 3: Persistent & Session-Based Shopping Cart
- **Hybrid Cart Engine:**
  - Unauthenticated users: Cart is maintained in Flask signed cookie session (`session['guest_cart']`).
  - Authenticated users: Cart is persisted in the `cart_items` table.
- **Global Context Injection:** The function `inject_global_data()` injects the total cart count dynamically into every Jinja2 template so the navigation badge updates across all pages.
- **Quantity Controls:** Quantity adjustments enforce upper bounds defined by the actual available inventory.

### 6.4 Module 4: Secure Checkout, Order Processing & Inventory Reduction
- **Server-Side Price Recalculation:** The server queries authoritative database prices for each product rather than trusting submitted client values.
- **Delivery Fee Policy:** Orders with items subtotal &ge; ₹999 receive **FREE Delivery**; orders below ₹999 incur a standard ₹99 shipping fee.
- **Transactional Atomic Fulfillment:**
  1. Validates that current stock &ge; requested quantity for all items.
  2. Generates a unique order number (`SE-YYYYMMDD-XXXXXX`).
  3. Inserts record into `orders`.
  4. Inserts immutable snapshots of name, image, and price into `order_items`.
  5. Decrements inventory in `products` (`stock = stock - quantity`).
  6. Purges user cart items in `cart_items`.
- **Cash on Delivery (COD):** Eliminates complex external payment gateways while providing an authentic checkout experience.

### 6.5 Module 5: Administrative Control Center & Analytics Dashboard
- **Executive KPI Cards:** Aggregates Total Revenue (summing non-cancelled orders), Total Orders placed, Total Products in inventory, Registered Customers count, and Low Stock Alerts count.
- **Product Management:** Full CRUD operations allowing administrators to publish products with images, edit attributes, restock inventory with quick inputs, or delete items.
- **Category Management:** Administrators can define new classifications with custom icons. Categories containing active products cannot be deleted accidentally (foreign key integrity safeguard).
- **Order Pipeline Manager:** Administrators can filter orders by status and transition customer purchases through fulfillment stages (*Pending &rarr; Processing &rarr; Shipped &rarr; Delivered &rarr; Cancelled*).

---

# 7. Security Analysis & Design Decisions

| Threat / Vulnerability | Risk | Mitigation in ShopEase |
|---|---|---|
| **SQL Injection (SQLi)** | High | 100% of queries use parameterized statements (`?` placeholders) through `cur.execute(query, params)`. No user input is concatenated into query strings. |
| **Credential Theft** | High | Passwords are never stored in plaintext. Passwords use PBKDF2 with SHA-256 and salt. |
| **Client-Side Price Tampering** | High | The checkout endpoint completely ignores client-submitted price totals, calculating amounts exclusively from database prices. |
| **Privilege Escalation** | Critical | Admin endpoints are protected by the `@admin_required` server decorator verifying `session.get('is_admin') == 1`. |
| **Cross-User Data Exposure (IDOR)** | Medium | Customer order viewing (`/order/<order_number>`) verifies that `order.user_id == session['user_id']` unless the user is an administrator. |
| **Inventory Overselling Race Condition** | High | Server-side validation inspects current stock levels inside a single transactional block before committing the order. |

---

# 8. Testing & Quality Assurance

### 8.1 Testing Methodology
The application was evaluated using Python's built-in `unittest` framework combined with Flask's test client (`app.test_client()`). The test suite simulates full HTTP client sessions, form submissions, session state verification, and database state assertions.

### 8.2 Test Suite Execution Matrix (10 Core Cases)

| Test ID | Test Case Objective | Input / Action | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **TC-01** | Customer Registration | POST `/register` with valid credentials | User created in `users` table; password hashed; `is_admin=0` | User stored; password securely hashed | **PASS** |
| **TC-02** | Customer Login | POST `/login` with registered credentials | Session established; redirected to home/dashboard | Session contains user info; redirected | **PASS** |
| **TC-03** | Product Discovery & Search | GET `/products?q=Watch` | Returns only items matching query keyword | "Ultra HD Smart Watch Pro" returned | **PASS** |
| **TC-04** | Cart Addition | POST `/cart/add/<id>` with quantity 2 | Item added to `cart_items`; badge increments | Cart count updated to 2 in DB | **PASS** |
| **TC-05** | Cart Quantity Update | POST `/cart/update/<id>` with quantity 3 | `cart_items.quantity` updated to 3; subtotal recalculates | Quantity updated; subtotal exact | **PASS** |
| **TC-06** | Checkout & Order Placement | POST `/checkout/place-order` with address & COD | Order created; line items snapshotted; stock decremented | Order placed; stock reduced; cart cleared | **PASS** |
| **TC-07** | Order History Display | GET `/orders` for logged in user | User's placed orders displayed with 'Pending' badge | Order displayed with status badge and details link | **PASS** |
| **TC-08** | Admin Access Control | POST `/login` as admin; GET `/admin` | Access granted to `/admin` dashboard | Admin metrics rendered | **PASS** |
| **TC-09** | Admin Product CRUD & Restock | POST `/admin/products/add`; POST `/update-stock` | Product published; stock updated to 75 | Product published; stock updated to 75 | **PASS** |
| **TC-10** | Order Status Transition | POST `/admin/orders/<id>/status` with 'Shipped' | Order status updated to 'Shipped' | Status updated successfully in DB | **PASS** |

### 8.3 Verification Results
The test suite script [test_portal.py](file:///c:/Users/ASUS/.gemini/antigravity/scratch/ShopEase/test_portal.py) executed all test scenarios with the following output:
```
Ran 9 tests in 1.225s
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
**Overall Test Score: 10 / 10 Requirements Verified (100% Pass Rate)**

---

# 9. User Interface Design & Screenshots Guide

Capture the following 13 screenshots from your browser at `http://127.0.0.1:5000` to accompany this report:

1. **Figure 1: Home Landing Page (`/`)** — Features the responsive top navigation, promotional hero banner, trust perks, category cards, and featured product grid.
2. **Figure 2: Product Catalog & Filtering (`/products`)** — Shows the category sidebar, price sorting dropdown, and multi-column product card layout.
3. **Figure 3: Keyword Search Results (`/products?q=watch`)** — Displays dynamic search filtering matching catalog product titles and descriptions.
4. **Figure 4: Product Detail Page (`/product/1`)** — Shows high-res imagery, rating stars, live stock status badge, and quantity selectors.
5. **Figure 5: Dynamic Shopping Cart (`/cart`)** — Shows line-item breakdown, quantity increment buttons, line subtotals, free shipping threshold alert, and order summary card.
6. **Figure 6: Customer Registration Page (`/register`)** — Shows the clean sign-up card with client/server validation.
7. **Figure 7: Secure Login Screen (`/login`)** — Shows authentication inputs, password toggle, and 1-click demo account buttons.
8. **Figure 8: Checkout Page (`/checkout`)** — Displays customer address fields, Cash on Delivery (COD) payment badge, and order summary.
9. **Figure 9: Order Confirmation Receipt (`/order/success/<order_number>`)** — Displays green success icon, generated Order Number, and estimated delivery timeline.
10. **Figure 10: Customer Order History (`/orders`)** — Shows previous orders with item count, total price in ₹, and color-coded status badges.
11. **Figure 11: Order Detail & Timeline (`/order/<order_number>`)** — Shows line item snapshots, shipping destination, and fulfillment progress.
12. **Figure 12: Admin Dashboard Analytics (`/admin`)** — Shows the 5 KPI metric cards (Total Sales, Orders, Products, Customers, Low Stock Alerts).
13. **Figure 13: Admin Inventory & Orders Management (`/admin/products` and `/admin/orders`)** — Shows the product management table with inline stock update and order status dropdown.

---

# 10. Conclusion & Future Enhancements

### 10.1 Conclusion
The **ShopEase** e-commerce portal provides a complete, modern online shopping experience that meets all functional and architectural requirements for a 3rd-year CSE project. By utilizing Flask and SQLite without unnecessary external dependencies, the system delivers high performance, clean code organization, and clear architectural boundaries that are easy to demonstrate and explain during evaluation.

### 10.2 Future Scope & Enhancements
- **Payment Gateway Integration:** Adding real-time online payment processors (e.g. Razorpay, UPI QR integration, Stripe).
- **Email Notifications:** Integrating SMTP services (Flask-Mail / SendGrid) for automated order confirmation and tracking emails.
- **Product Reviews & Ratings:** Permitting verified buyers to submit star reviews and upload customer photos.
- **RESTful API Service:** Exposing JSON endpoints with JWT authentication for a potential React Native or Flutter mobile application.

---

# 11. References & Bibliography

1. **Flask Documentation (v3.1):** Pallets Projects. *Flask: Web development, one drop at a time.* [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
2. **SQLite Documentation:** SQLite Consortium. *SQLite: An In-Process Database Engine.* [https://www.sqlite.org/docs.html](https://www.sqlite.org/docs.html)
3. **Werkzeug Security Utilities:** Pallets Projects. *Password Hashing & Cryptography.* [https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security](https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security)
4. **Jinja2 Templating Engine:** Pallets Projects. *Jinja Template Designer Documentation.* [https://jinja.palletsprojects.com/](https://jinja.palletsprojects.com/)
5. **Mozilla Developer Network (MDN):** *Web Security Guidelines, HTTP Session Cookies & DOM Manipulation.* [https://developer.mozilla.org/](https://developer.mozilla.org/)

---

# 12. Appendix: College Evaluation Viva Q&A Guide

### Q1: What architectural pattern does ShopEase use?
> **Answer:** ShopEase follows the **Model-Template-View (MTV)** pattern. SQLite tables represent the Data Model; HTML templates styled with CSS represent the Templates; and Flask route functions in `app.py` act as the Views/Controllers handling business logic, session validation, and database operations.

### Q2: How is password security implemented?
> **Answer:** Passwords are never saved in plaintext. During registration, `generate_password_hash()` generates a salted PBKDF2 hash using SHA-256. During login, `check_password_hash()` verifies the entered password against the stored cryptographic hash in constant time, preventing timing attacks.

### Q3: How does ShopEase protect against SQL Injection?
> **Answer:** All database queries in `database.py` and `app.py` use **parameterized queries** with `?` placeholders (e.g. `cur.execute("SELECT * FROM users WHERE email = ?", (email,))`). The database driver treats user input strictly as literal values rather than executable SQL commands.

### Q4: Why is purchase-time price snapshotting important?
> **Answer:** If an e-commerce platform links order items directly to the product's live price in the catalog, any future price increase or discount would retroactively alter past customer receipts. In ShopEase, the `order_items` table stores an immutable snapshot of the product name, image, and unit price at the moment of order placement.

### Q5: How are guest cart items handled when a user logs in?
> **Answer:** When an unauthenticated visitor adds items to their cart, selections are saved in `session['guest_cart']`. When the user logs in, `merge_guest_cart_to_db()` inspects the session cart, verifies available warehouse stock, and inserts or updates those items in the user's database cart table (`cart_items`).
