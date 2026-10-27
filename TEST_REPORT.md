# ShopEase - Test Plan, Execution Report & Screenshot Guide
### TA-2 Evaluation & Project Documentation

This document provides the formal test plan, verification results, and an exact checklist of screenshots to include in your final college project report.

---

## Part 1: Automated Test Execution Report

The test suite was executed via `python test_portal.py` against the active Flask application and SQLite database:

| Test ID | Test Scenario | Input Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **TC-01** | Customer Registration | Name: Anita Desai, Email: `anita@test.com`, Password: `password123` | New user created in `users` table with hashed password, `is_admin=0` | User record created, password securely hashed | **PASS** |
| **TC-02** | Customer Login | Email: `user@shopease.com`, Password: `user123` | Session initialized (`user_id`, `user_email`, `is_admin=False`), redirected to home | Session created, user name shown in navbar | **PASS** |
| **TC-03** | Product Catalog Search & Category Filter | Query: "Watch", Category ID: 1 (Electronics) | Returns products matching search query and category | "Ultra HD Smart Watch Pro" returned; category filtered correctly | **PASS** |
| **TC-04** | Add to Shopping Cart | Product ID: 1, Quantity: 2 | Item added to `cart_items` table, cart badge counter increments | Record inserted in DB, cart counter displays 2 | **PASS** |
| **TC-05** | Update Cart Item Quantity | Product ID: 1, New Quantity: 3 | `cart_items.quantity` updated to 3; subtotal recalculated | Quantity updated to 3, subtotal accurately computed | **PASS** |
| **TC-06** | Checkout & Order Placement | Customer details + Cash on Delivery payment | Order recorded in `orders` and `order_items`; cart cleared; stock decremented | Order placed with unique order number; product stock reduced by 2; cart empty | **PASS** |
| **TC-07** | Order History Display | Logged-in Customer navigating to `/orders` | Order appears in table with order number, date, amount, and 'Pending' badge | Order displayed with status badge and details link | **PASS** |
| **TC-08** | Admin Authentication & RBAC | Email: `admin@shopease.com`, Password: `admin123` | `is_admin=True` in session; `/admin` dashboard accessible | Admin verified; redirected to `/admin` with full metrics | **PASS** |
| **TC-09** | Admin Product CRUD & Restock | Add: "Wireless Ergonomic Mouse", Stock: 40 &rarr; Update to 75 | New product inserted into catalog; stock updated to 75 | Product published; stock verified at 75 | **PASS** |
| **TC-10** | Admin Order Status Transition | Order ID: Target order, New Status: 'Shipped' | `orders.status` updated from 'Pending' to 'Shipped' | Status updated successfully, audit confirmed | **PASS** |

**Summary: 10 Passed, 0 Failed, 0 Blocked (100% Success Rate)**

---

## Part 2: Curated Screenshot Guide for College Report

Capture the following 12 key screenshots from your browser at `http://127.0.0.1:5000` to include in your project documentation:

### Screenshot 1: Home Landing Page
- **URL:** `http://127.0.0.1:5000/`
- **What to show:**
  - Sticky navigation bar with ShopEase logo, global search input, category bar, and cart badge.
  - Dark modern Hero Banner with call-to-action buttons.
  - Perks & Trust Badges (Free Delivery, Cash on Delivery, 7-Day Returns).
  - Popular Categories grid with circular icon badges.
  - Featured Products collection cards.
- **Report Caption:** *Figure 1: ShopEase Home Page with Responsive Navigation & Promotional Banners*

---

### Screenshot 2: Product Catalog & Multi-Criteria Filtering
- **URL:** `http://127.0.0.1:5000/products`
- **What to show:**
  - Left sidebar with category filters and sorting options (Newest, Price: Low to High, etc.).
  - Main product grid displaying product cards with image, price in ₹, stock badge, and Add to Cart icon.
- **Report Caption:** *Figure 2: Product Catalog with Category Filtering and Price Sorting*

---

### Screenshot 3: Product Search Results
- **URL:** `http://127.0.0.1:5000/products?q=watch`
- **What to show:**
  - Search query header: *Showing 1 products matching "watch"*.
  - Matching product card for "Ultra HD Smart Watch Pro".
- **Report Caption:** *Figure 3: Keyword Search Functionality across Catalog Names and Descriptions*

---

### Screenshot 4: Product Detail Page
- **URL:** `http://127.0.0.1:5000/product/1`
- **What to show:**
  - High-resolution product image.
  - Star ratings, category breadcrumb, and price.
  - Stock availability indicator badge (*In Stock - X units available*).
  - Quantity selector buttons (`-` and `+`).
  - "Add to Cart" and "View Cart" CTA buttons.
  - Related products showcase at the bottom.
- **Report Caption:** *Figure 4: Product Detail View with Inventory Indicator and Quantity Selector*

---

### Screenshot 5: Interactive Shopping Cart
- **URL:** `http://127.0.0.1:5000/cart`
- **What to show:**
  - Itemized table showing thumbnail, product title, unit price, quantity increment controls, item subtotal, and remove trash icon.
  - Right sidebar Order Summary card showing Items Subtotal, Shipping Fee (with Free Delivery notice), and Grand Total.
  - "Proceed to Checkout" button.
- **Report Caption:** *Figure 5: Dynamic Shopping Cart with Line Item Calculation and Delivery Fee Waiver*

---

### Screenshot 6: User Registration Page
- **URL:** `http://127.0.0.1:5000/register`
- **What to show:**
  - Clean registration card with Full Name, Email, Password, Confirm Password, Phone, and Address inputs.
  - Server validation hints and link to Sign In.
- **Report Caption:** *Figure 6: Customer Registration Screen with Password Hashing Validation*

---

### Screenshot 7: User Login & 1-Click Demo Credentials
- **URL:** `http://127.0.0.1:5000/login`
- **What to show:**
  - Login card with email and password fields.
  - Eye icon password visibility toggle.
  - Highlighted **Demo Accounts box** with 1-click buttons (*Customer: user@shopease.com* and *Admin: admin@shopease.com*).
- **Report Caption:** *Figure 7: Secure Authentication Screen with Role Detection and Quick-Fill Helpers*

---

### Screenshot 8: Checkout & Delivery Address Form
- **URL:** `http://127.0.0.1:5000/checkout`
- **What to show:**
  - Pre-filled customer contact and shipping address form.
  - Cash on Delivery (COD) payment method highlighted with *Zero Extra Fee* badge.
  - Order summary sidebar previewing line items and final payable amount.
- **Report Caption:** *Figure 8: Checkout Page with Delivery Address Validation and Cash on Delivery Option*

---

### Screenshot 9: Order Confirmation Screen
- **URL:** `http://127.0.0.1:5000/order/success/<order_number>`
- **What to show:**
  - Green circular success checkmark.
  - Generated alphanumeric Order Number (e.g. `SE-20261028-XXXX`).
  - Estimated delivery timeline (3-5 business days).
  - Shipping address summary and order breakdown.
- **Report Caption:** *Figure 9: Order Confirmation Receipt with Unique Order ID and Delivery Estimate*

---

### Screenshot 10: Customer Order History
- **URL:** `http://127.0.0.1:5000/orders`
- **What to show:**
  - List of past orders with Order Number, Date Placed, Item Count, Total Amount in ₹, and color-coded Status Badges (*Pending*, *Processing*, *Shipped*, *Delivered*).
  - "Details" button for each order.
- **Report Caption:** *Figure 10: Customer Order History Tracking with Real-Time Fulfillment Status Badges*

---

### Screenshot 11: Admin Dashboard Analytics
- **URL:** `http://127.0.0.1:5000/admin`
- **What to show:**
  - Five KPI metric cards: Total Sales Revenue (₹), Total Orders, Catalog Products, Registered Customers, and Low Stock Alerts.
  - Recent Customer Orders table with inline status dropdown.
  - Inventory Watchlist showing items with stock < 10.
- **Report Caption:** *Figure 11: Administrative Control Center with Key Performance Indicators (KPIs)*

---

### Screenshot 12: Admin Product Inventory Management
- **URL:** `http://127.0.0.1:5000/admin/products`
- **What to show:**
  - Table of all inventory items with image thumbnails, category tags, price, and inline stock input with quick-save checkmark.
  - "Add New Product" CTA button.
  - Edit and Delete action buttons.
- **Report Caption:** *Figure 12: Admin Inventory Manager with Inline Stock Restocking Controls*

---

### Screenshot 13: Admin Order Status Manager
- **URL:** `http://127.0.0.1:5000/admin/orders`
- **What to show:**
  - Status filter pill tabs: *All, Pending, Processing, Shipped, Delivered, Cancelled* with live counts.
  - Orders table with customer contact details, items count, total amount, and quick status update dropdown.
- **Report Caption:** *Figure 13: Order Fulfillment Dashboard with State Transition Controls*
