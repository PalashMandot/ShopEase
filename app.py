"""
app.py - ShopEase E-Commerce Web Portal
Main Flask Application containing routes, authentication, catalog, cart,
checkout, order processing, and administrative dashboard.

Developed for College CSE Project / TA-2 Evaluation.
"""

import os
import uuid
import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, query_db, execute_db, init_db, seed_data

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'shopease-college-ta2-secret-key-cse-2026')

# Automatically ensure database and sample data are ready
with app.app_context():
    init_db()
    seed_data()


# -----------------------------------------------------------------------------
# ACCESS CONTROL DECORATORS
# -----------------------------------------------------------------------------

def login_required(f):
    """Decorator ensuring that only authenticated users can access the endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator ensuring that only administrators can access the endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Administrator login required.', 'warning')
            return redirect(url_for('login', next=request.url))
        if not session.get('is_admin'):
            flash('Access denied. You do not have administrator permissions.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# -----------------------------------------------------------------------------
# CONTEXT PROCESSORS (Available in all Jinja templates)
# -----------------------------------------------------------------------------

@app.context_processor
def inject_global_data():
    """Provides categories, cart count, and current year to all templates."""
    categories = query_db("SELECT * FROM categories ORDER BY name ASC")
    
    # Calculate cart count
    cart_count = 0
    if 'user_id' in session:
        row = query_db(
            "SELECT COALESCE(SUM(quantity), 0) as total FROM cart_items WHERE user_id = ?",
            (session['user_id'],),
            one=True
        )
        if row:
            cart_count = row['total']
    else:
        guest_cart = session.get('guest_cart', {})
        cart_count = sum(guest_cart.values())

    return {
        'all_categories': categories,
        'cart_count': cart_count,
        'current_year': datetime.datetime.now().year
    }


# -----------------------------------------------------------------------------
# CART HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def get_user_cart_items():
    """
    Retrieves full cart items for currently logged in user or guest session.
    Calculates item subtotals, cart subtotal, shipping fee, and grand total.
    """
    items = []
    subtotal = 0.0

    if 'user_id' in session:
        # Load from SQLite database
        rows = query_db('''
            SELECT c.id as cart_id, c.quantity, p.id as product_id, p.name,
                   p.price, p.stock, p.image_url, cat.name as category_name
            FROM cart_items c
            JOIN products p ON c.product_id = p.id
            JOIN categories cat ON p.category_id = cat.id
            WHERE c.user_id = ?
            ORDER BY c.created_at DESC
        ''', (session['user_id'],))

        for row in rows:
            item_subtotal = row['price'] * row['quantity']
            subtotal += item_subtotal
            items.append({
                'cart_id': row['cart_id'],
                'product_id': row['product_id'],
                'name': row['name'],
                'price': row['price'],
                'stock': row['stock'],
                'image_url': row['image_url'],
                'category_name': row['category_name'],
                'quantity': row['quantity'],
                'subtotal': item_subtotal
            })
    else:
        # Guest cart from Flask session
        guest_cart = session.get('guest_cart', {})
        if guest_cart:
            product_ids = list(guest_cart.keys())
            placeholders = ','.join(['?'] * len(product_ids))
            rows = query_db(f'''
                SELECT p.id as product_id, p.name, p.price, p.stock, p.image_url, cat.name as category_name
                FROM products p
                JOIN categories cat ON p.category_id = cat.id
                WHERE p.id IN ({placeholders})
            ''', product_ids)

            for row in rows:
                pid = str(row['product_id'])
                qty = guest_cart.get(pid, 1)
                item_subtotal = row['price'] * qty
                subtotal += item_subtotal
                items.append({
                    'cart_id': None,
                    'product_id': row['product_id'],
                    'name': row['name'],
                    'price': row['price'],
                    'stock': row['stock'],
                    'image_url': row['image_url'],
                    'category_name': row['category_name'],
                    'quantity': qty,
                    'subtotal': item_subtotal
                })

    # Business rule: Free shipping for orders above ₹999, else ₹99
    shipping_fee = 0.0 if (subtotal >= 999 or subtotal == 0) else 99.0
    total_amount = subtotal + shipping_fee

    return {
        'items': items,
        'cart_items': items,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'total_amount': total_amount
    }


def merge_guest_cart_to_db(user_id):
    """Merges guest session cart into database when user logs in."""
    guest_cart = session.get('guest_cart', {})
    if not guest_cart:
        return

    for pid_str, qty in guest_cart.items():
        try:
            pid = int(pid_str)
            existing = query_db(
                "SELECT id, quantity FROM cart_items WHERE user_id = ? AND product_id = ?",
                (user_id, pid),
                one=True
            )
            # Check stock
            prod = query_db("SELECT stock FROM products WHERE id = ?", (pid,), one=True)
            if not prod:
                continue

            max_stock = prod['stock']
            if existing:
                new_qty = min(existing['quantity'] + qty, max_stock)
                execute_db("UPDATE cart_items SET quantity = ? WHERE id = ?", (new_qty, existing['id']))
            else:
                new_qty = min(qty, max_stock)
                if new_qty > 0:
                    execute_db(
                        "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
                        (user_id, pid, new_qty)
                    )
        except Exception:
            continue

    session.pop('guest_cart', None)


# -----------------------------------------------------------------------------
# MODULE 1: USER AUTHENTICATION & PROFILE
# -----------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration route with form validation and password hashing."""
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        # Validation checks
        if not name or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        # Check existing email
        existing_user = query_db("SELECT id FROM users WHERE email = ?", (email,), one=True)
        if existing_user:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        # Secure password hashing with werkzeug
        hashed_pw = generate_password_hash(password)

        new_user_id = execute_db('''
            INSERT INTO users (name, email, password_hash, phone, address, is_admin)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (name, email, hashed_pw, phone, address))

        flash('Registration successful! Please log in to start shopping.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User and admin login with session establishment and role identification."""
    if 'user_id' in session:
        if session.get('is_admin'):
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))

    next_url = request.args.get('next')

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')

        user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)

        if user and check_password_hash(user['password_hash'], password):
            # Establish session
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['is_admin'] = bool(user['is_admin'])

            # Merge any items added before logging in
            merge_guest_cart_to_db(user['id'])

            flash(f'Welcome back, {user["name"]}!', 'success')

            # Route to admin panel if administrator
            if user['is_admin']:
                return redirect(next_url or url_for('admin_dashboard'))

            return redirect(next_url or url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html', next=next_url)


@app.route('/logout')
def logout():
    """Clears user session and logs out."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Customer profile page to view account details and update shipping info."""
    user = query_db("SELECT * FROM users WHERE id = ?", (session['user_id'],), one=True)
    if not user:
        session.clear()
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        if not name:
            flash('Name cannot be empty.', 'danger')
        else:
            execute_db('''
                UPDATE users SET name = ?, phone = ?, address = ? WHERE id = ?
            ''', (name, phone, address, session['user_id']))
            session['user_name'] = name
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))

    # Profile statistics
    order_stats = query_db('''
        SELECT COUNT(*) as total_orders, COALESCE(SUM(total_amount), 0) as total_spent
        FROM orders WHERE user_id = ? AND status != 'Cancelled'
    ''', (session['user_id'],), one=True)

    recent_orders = query_db('''
        SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 5
    ''', (session['user_id'],))

    return render_template('profile.html', user=user, stats=order_stats, recent_orders=recent_orders)


# -----------------------------------------------------------------------------
# MODULE 2: PRODUCT CATALOG, SEARCH & FILTER
# -----------------------------------------------------------------------------

@app.route('/')
def index():
    """Home landing page featuring hero banners, categories, and trending products."""
    featured_products = query_db('''
        SELECT p.*, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.featured = 1 AND p.stock > 0
        ORDER BY p.id DESC LIMIT 8
    ''')

    latest_products = query_db('''
        SELECT p.*, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.stock > 0
        ORDER BY p.id DESC LIMIT 8
    ''')

    categories = query_db('''
        SELECT c.*, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id
        GROUP BY c.id
        ORDER BY c.name ASC
    ''')

    return render_template(
        'index.html',
        featured_products=featured_products,
        latest_products=latest_products,
        categories_with_count=categories
    )


@app.route('/products')
def products():
    """
    Catalog page with keyword search, category filtering, and price/recency sorting.
    """
    search_query = request.args.get('q', '').strip()
    category_id = request.args.get('category')
    sort_by = request.args.get('sort', 'newest')

    query = '''
        SELECT p.*, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE 1=1
    '''
    params = []

    # Filter by search keyword in name or description
    if search_query:
        query += " AND (p.name LIKE ? OR p.description LIKE ?)"
        wildcard = f"%{search_query}%"
        params.extend([wildcard, wildcard])

    # Filter by category
    selected_category = None
    if category_id and category_id.isdigit():
        query += " AND p.category_id = ?"
        params.append(int(category_id))
        selected_category = query_db("SELECT * FROM categories WHERE id = ?", (category_id,), one=True)

    # Sorting
    if sort_by == 'price_asc':
        query += " ORDER BY p.price ASC"
    elif sort_by == 'price_desc':
        query += " ORDER BY p.price DESC"
    elif sort_by == 'name_asc':
        query += " ORDER BY p.name ASC"
    else:  # newest
        query += " ORDER BY p.id DESC"

    product_list = query_db(query, params)

    return render_template(
        'products.html',
        products=product_list,
        search_query=search_query,
        selected_category=selected_category,
        current_sort=sort_by
    )


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page displaying full descriptions, stock status, and related items."""
    product = query_db('''
        SELECT p.*, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.id = ?
    ''', (product_id,), one=True)

    if not product:
        flash('Product not found.', 'warning')
        return redirect(url_for('products'))

    # Related products from same category
    related_products = query_db('''
        SELECT p.*, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.category_id = ? AND p.id != ? AND p.stock > 0
        LIMIT 4
    ''', (product['category_id'], product_id))

    return render_template('product_detail.html', product=product, related_products=related_products)


# -----------------------------------------------------------------------------
# MODULE 3: SHOPPING CART
# -----------------------------------------------------------------------------

@app.route('/cart')
def cart():
    """Displays the user's current shopping cart and order subtotal breakdown."""
    cart_data = get_user_cart_items()
    return render_template('cart.html', cart=cart_data)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """
    Adds a product to cart or increments existing quantity with stock validation.
    Accepts standard form submit or AJAX JSON requests.
    """
    # Verify product and stock
    product = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    if not product:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        flash('Product not found.', 'danger')
        return redirect(url_for('products'))

    try:
        qty = int(request.form.get('quantity', 1))
        if qty < 1:
            qty = 1
    except ValueError:
        qty = 1

    if product['stock'] < 1:
        if request.is_json:
            return jsonify({'success': False, 'message': 'This product is out of stock.'}), 400
        flash('Sorry, this product is currently out of stock.', 'danger')
        return redirect(url_for('product_detail', product_id=product_id))

    # Logged-in user: database-backed cart
    if 'user_id' in session:
        user_id = session['user_id']
        existing = query_db(
            "SELECT id, quantity FROM cart_items WHERE user_id = ? AND product_id = ?",
            (user_id, product_id),
            one=True
        )

        if existing:
            new_qty = existing['quantity'] + qty
            if new_qty > product['stock']:
                new_qty = product['stock']
                msg = f'Maximum available stock of {product["stock"]} reached for {product["name"]}.'
            else:
                msg = f'Added {qty} more of {product["name"]} to your cart!'

            execute_db("UPDATE cart_items SET quantity = ? WHERE id = ?", (new_qty, existing['id']))
        else:
            if qty > product['stock']:
                qty = product['stock']
            execute_db(
                "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
                (user_id, product_id, qty)
            )
            msg = f'Added {product["name"]} to your cart!'
    else:
        # Guest user: session-backed cart
        guest_cart = session.get('guest_cart', {})
        pid_str = str(product_id)
        current_qty = guest_cart.get(pid_str, 0)
        new_qty = current_qty + qty

        if new_qty > product['stock']:
            new_qty = product['stock']
            msg = f'Maximum stock reached for {product["name"]}.'
        else:
            msg = f'Added {product["name"]} to your cart!'

        guest_cart[pid_str] = new_qty
        session['guest_cart'] = guest_cart
        session.modified = True

    if request.is_json:
        # Return updated cart count
        cart_data = get_user_cart_items()
        return jsonify({
            'success': True,
            'message': msg,
            'cart_count': sum(item['quantity'] for item in cart_data['items'])
        })

    flash(msg, 'success')
    return redirect(request.referrer or url_for('cart'))


@app.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    """
    Updates item quantity in cart. If quantity is 0, item is removed.
    Validates against maximum warehouse stock.
    """
    try:
        new_qty = int(request.form.get('quantity', 1))
    except ValueError:
        new_qty = 1

    product = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('cart'))

    if new_qty <= 0:
        return remove_from_cart(product_id)

    # Cap at available stock
    if new_qty > product['stock']:
        new_qty = product['stock']
        flash(f'Adjusted to maximum available stock ({product["stock"]}) for {product["name"]}.', 'warning')

    if 'user_id' in session:
        execute_db(
            "UPDATE cart_items SET quantity = ? WHERE user_id = ? AND product_id = ?",
            (new_qty, session['user_id'], product_id)
        )
    else:
        guest_cart = session.get('guest_cart', {})
        guest_cart[str(product_id)] = new_qty
        session['guest_cart'] = guest_cart
        session.modified = True

    flash('Cart updated successfully.', 'success')
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    """Removes an item from the shopping cart."""
    if 'user_id' in session:
        execute_db(
            "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
            (session['user_id'], product_id)
        )
    else:
        guest_cart = session.get('guest_cart', {})
        guest_cart.pop(str(product_id), None)
        session['guest_cart'] = guest_cart
        session.modified = True

    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))


@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    """Clears all items from the current cart."""
    if 'user_id' in session:
        execute_db("DELETE FROM cart_items WHERE user_id = ?", (session['user_id'],))
    else:
        session.pop('guest_cart', None)

    flash('Your cart has been cleared.', 'info')
    return redirect(url_for('cart'))


# -----------------------------------------------------------------------------
# MODULE 4: CHECKOUT & ORDERS
# -----------------------------------------------------------------------------

@app.route('/checkout')
@login_required
def checkout():
    """
    Checkout page showing order summary, customer shipping address,
    and Cash on Delivery payment option.
    """
    cart_data = get_user_cart_items()
    if not cart_data['items']:
        flash('Your cart is empty. Please add items before checking out.', 'warning')
        return redirect(url_for('products'))

    user = query_db("SELECT * FROM users WHERE id = ?", (session['user_id'],), one=True)
    return render_template('checkout.html', cart=cart_data, user=user)


@app.route('/checkout/place-order', methods=['POST'])
@login_required
def place_order():
    """
    Places order with server-side stock and price validation.
    Snapshots product details in order_items table and decreases inventory.
    Uses Cash on Delivery as specified.
    """
    user_id = session['user_id']
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    cart_data = get_user_cart_items()

    if not cart_data['items']:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('products'))

    # Form parameters
    name = request.form.get('customer_name', '').strip() or user['name']
    phone = request.form.get('customer_phone', '').strip() or user['phone']
    address = request.form.get('shipping_address', '').strip()
    city = request.form.get('city', '').strip()
    postal_code = request.form.get('postal_code', '').strip()
    order_notes = request.form.get('order_notes', '').strip()

    if not name or not phone or not address or not city or not postal_code:
        flash('Please fill in all required shipping and contact details.', 'danger')
        return redirect(url_for('checkout'))

    # Strict Server-Side Validation: check stock availability for all items before placing
    conn = get_db()
    cur = conn.cursor()

    try:
        for item in cart_data['items']:
            prod = cur.execute(
                "SELECT stock, name FROM products WHERE id = ?", (item['product_id'],)
            ).fetchone()

            if not prod or prod['stock'] < item['quantity']:
                avail = prod['stock'] if prod else 0
                flash(f'Cannot place order: Only {avail} units of "{item["name"]}" are available.', 'danger')
                conn.close()
                return redirect(url_for('cart'))

        # Generate unique order number (e.g. SE-20261028-A1B2)
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        random_suffix = uuid.uuid4().hex[:6].upper()
        order_number = f"SE-{date_str}-{random_suffix}"

        # 1. Insert into orders table
        cur.execute('''
            INSERT INTO orders (
                order_number, user_id, customer_name, customer_email,
                customer_phone, shipping_address, city, postal_code,
                order_notes, payment_method, subtotal, shipping_fee,
                total_amount, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Cash on Delivery', ?, ?, ?, 'Pending')
        ''', (
            order_number, user_id, name, user['email'],
            phone, address, city, postal_code,
            order_notes, cart_data['subtotal'], cart_data['shipping_fee'],
            cart_data['total_amount']
        ))

        order_id = cur.lastrowid

        # 2. Insert line items snapshotting purchase prices & reduce product inventory
        for item in cart_data['items']:
            cur.execute('''
                INSERT INTO order_items (
                    order_id, product_id, product_name, product_image,
                    price, quantity, subtotal
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id, item['product_id'], item['name'], item['image_url'],
                item['price'], item['quantity'], item['subtotal']
            ))

            # Reduce product stock
            cur.execute('''
                UPDATE products SET stock = stock - ? WHERE id = ?
            ''', (item['quantity'], item['product_id']))

        # 3. Clear user's shopping cart
        cur.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'An error occurred while placing your order: {str(e)}', 'danger')
        return redirect(url_for('cart'))

    conn.close()
    flash('Congratulations! Your order has been placed successfully.', 'success')
    return redirect(url_for('order_success', order_number=order_number))


@app.route('/order/success/<order_number>')
@login_required
def order_success(order_number):
    """Displays order confirmation page with order summary and estimated delivery."""
    order = query_db(
        "SELECT * FROM orders WHERE order_number = ? AND user_id = ?",
        (order_number, session['user_id']),
        one=True
    )
    if not order:
        flash('Order not found.', 'warning')
        return redirect(url_for('orders'))

    items = query_db("SELECT * FROM order_items WHERE order_id = ?", (order['id'],))
    return render_template('order_success.html', order=order, items=items)


@app.route('/orders')
@login_required
def orders():
    """Customer order history page listing all past purchases with status badges."""
    user_orders = query_db('''
        SELECT o.*, COUNT(oi.id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.user_id = ?
        GROUP BY o.id
        ORDER BY o.created_at DESC
    ''', (session['user_id'],))

    return render_template('orders.html', orders=user_orders)


@app.route('/order/<order_number>')
@login_required
def order_detail(order_number):
    """
    Detailed breakdown of an order: shipping address, payment method,
    status timeline, and individual items.
    Ensures users can only view their own orders unless they are an admin.
    """
    order = query_db("SELECT * FROM orders WHERE order_number = ?", (order_number,), one=True)
    if not order:
        flash('Order not found.', 'warning')
        return redirect(url_for('orders'))

    # Security check: User must own the order or be an admin
    if order['user_id'] != session['user_id'] and not session.get('is_admin'):
        flash('Unauthorized access to this order.', 'danger')
        return redirect(url_for('orders'))

    items = query_db("SELECT * FROM order_items WHERE order_id = ?", (order['id'],))
    return render_template('order_detail.html', order=order, items=items)


# -----------------------------------------------------------------------------
# MODULE 5: ADMIN DASHBOARD & MANAGEMENT
# -----------------------------------------------------------------------------

@app.route('/admin')
@admin_required
def admin_dashboard():
    """
    Admin control center displaying key performance metrics:
    total sales, total orders, total products, registered users,
    and recent customer orders.
    """
    # 1. KPI Statistics
    total_sales = query_db(
        "SELECT COALESCE(SUM(total_amount), 0) as total FROM orders WHERE status != 'Cancelled'",
        one=True
    )['total']

    total_orders = query_db("SELECT COUNT(*) as count FROM orders", one=True)['count']
    total_products = query_db("SELECT COUNT(*) as count FROM products", one=True)['count']
    total_users = query_db("SELECT COUNT(*) as count FROM users WHERE is_admin = 0", one=True)['count']
    low_stock_count = query_db("SELECT COUNT(*) as count FROM products WHERE stock < 10", one=True)['count']

    # 2. Recent Orders
    recent_orders = query_db('''
        SELECT o.*, u.name as user_name
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC LIMIT 8
    ''')

    # 3. Low Stock Alert Products
    low_stock_products = query_db('''
        SELECT p.*, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.stock < 10
        ORDER BY p.stock ASC LIMIT 5
    ''')

    return render_template(
        'admin/dashboard.html',
        total_sales=total_sales,
        total_orders=total_orders,
        total_products=total_products,
        total_users=total_users,
        low_stock_count=low_stock_count,
        recent_orders=recent_orders,
        low_stock_products=low_stock_products
    )


@app.route('/admin/products')
@admin_required
def admin_products():
    """List of all inventory products with management controls."""
    search_query = request.args.get('q', '').strip()
    category_id = request.args.get('category')

    query = '''
        SELECT p.*, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE 1=1
    '''
    params = []

    if search_query:
        query += " AND (p.name LIKE ? OR p.description LIKE ?)"
        wildcard = f"%{search_query}%"
        params.extend([wildcard, wildcard])

    if category_id and category_id.isdigit():
        query += " AND p.category_id = ?"
        params.append(int(category_id))

    query += " ORDER BY p.id DESC"
    all_products = query_db(query, params)
    categories = query_db("SELECT * FROM categories ORDER BY name ASC")

    return render_template(
        'admin/products.html',
        products=all_products,
        categories=categories,
        search_query=search_query,
        selected_category=int(category_id) if category_id and category_id.isdigit() else None
    )


@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    """Admin endpoint to create a new product."""
    categories = query_db("SELECT * FROM categories ORDER BY name ASC")

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id')
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        stock = request.form.get('stock', '').strip()
        image_url = request.form.get('image_url', '').strip()
        featured = 1 if request.form.get('featured') else 0

        # Form validation
        if not name or not category_id or not price or not stock or not description:
            flash('Please fill in all required fields.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=None)

        try:
            price_val = float(price)
            stock_val = int(stock)
            if price_val < 0 or stock_val < 0:
                raise ValueError
        except ValueError:
            flash('Price and stock must be valid non-negative numbers.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=None)

        if not image_url:
            # Fallback placeholder image
            image_url = 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80'

        execute_db('''
            INSERT INTO products (category_id, name, description, price, stock, image_url, featured)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (category_id, name, description, price_val, stock_val, image_url, featured))

        flash(f'Product "{name}" added successfully!', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/product_form.html', categories=categories, product=None)


@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    """Admin endpoint to edit an existing product."""
    product = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin_products'))

    categories = query_db("SELECT * FROM categories ORDER BY name ASC")

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id')
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        stock = request.form.get('stock', '').strip()
        image_url = request.form.get('image_url', '').strip()
        featured = 1 if request.form.get('featured') else 0

        if not name or not category_id or not price or not stock or not description:
            flash('Please fill in all required fields.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=product)

        try:
            price_val = float(price)
            stock_val = int(stock)
            if price_val < 0 or stock_val < 0:
                raise ValueError
        except ValueError:
            flash('Price and stock must be non-negative numbers.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=product)

        if not image_url:
            image_url = product['image_url']

        execute_db('''
            UPDATE products
            SET category_id = ?, name = ?, description = ?, price = ?, stock = ?, image_url = ?, featured = ?
            WHERE id = ?
        ''', (category_id, name, description, price_val, stock_val, image_url, featured, product_id))

        flash(f'Product "{name}" updated successfully!', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/product_form.html', categories=categories, product=product)


@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    """Admin endpoint to delete a product from inventory."""
    product = query_db("SELECT name FROM products WHERE id = ?", (product_id,), one=True)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin_products'))

    try:
        execute_db("DELETE FROM products WHERE id = ?", (product_id,))
        flash(f'Product "{product["name"]}" deleted successfully.', 'success')
    except Exception as e:
        flash(f'Could not delete product: {str(e)}', 'danger')

    return redirect(url_for('admin_products'))


@app.route('/admin/products/update-stock/<int:product_id>', methods=['POST'])
@admin_required
def admin_update_stock(product_id):
    """Quick inline stock level update."""
    try:
        new_stock = int(request.form.get('stock', 0))
        if new_stock < 0:
            new_stock = 0
        execute_db("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
        flash('Stock updated successfully.', 'success')
    except ValueError:
        flash('Invalid stock value.', 'danger')

    return redirect(request.referrer or url_for('admin_products'))


@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def admin_categories():
    """Manage product categories: view, add, and remove categories."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', 'bi-tag').strip()

        if not name:
            flash('Category name is required.', 'danger')
        else:
            existing = query_db("SELECT id FROM categories WHERE name = ?", (name,), one=True)
            if existing:
                flash('A category with this name already exists.', 'warning')
            else:
                execute_db(
                    "INSERT INTO categories (name, description, icon) VALUES (?, ?, ?)",
                    (name, description, icon)
                )
                flash(f'Category "{name}" added successfully!', 'success')
                return redirect(url_for('admin_categories'))

    categories = query_db('''
        SELECT c.*, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id
        GROUP BY c.id
        ORDER BY c.name ASC
    ''')
    return render_template('admin/categories.html', categories=categories)


@app.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def admin_delete_category(category_id):
    """Delete category only if no products are linked."""
    product_count = query_db(
        "SELECT COUNT(*) as count FROM products WHERE category_id = ?",
        (category_id,),
        one=True
    )['count']

    if product_count > 0:
        flash(f'Cannot delete category: {product_count} product(s) are still assigned to it.', 'danger')
    else:
        execute_db("DELETE FROM categories WHERE id = ?", (category_id,))
        flash('Category deleted successfully.', 'success')

    return redirect(url_for('admin_categories'))


@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Admin view of all customer orders with filtering by status."""
    status_filter = request.args.get('status', 'All')

    if status_filter != 'All':
        orders_list = query_db('''
            SELECT o.*, u.name as customer_name_user, COUNT(oi.id) as item_count
            FROM orders o
            JOIN users u ON o.user_id = u.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status = ?
            GROUP BY o.id
            ORDER BY o.created_at DESC
        ''', (status_filter,))
    else:
        orders_list = query_db('''
            SELECT o.*, u.name as customer_name_user, COUNT(oi.id) as item_count
            FROM orders o
            JOIN users u ON o.user_id = u.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id
            ORDER BY o.created_at DESC
        ''')

    # Get status counts for filter pills
    status_counts = {
        'All': query_db("SELECT COUNT(*) as count FROM orders", one=True)['count'],
        'Pending': query_db("SELECT COUNT(*) as count FROM orders WHERE status = 'Pending'", one=True)['count'],
        'Processing': query_db("SELECT COUNT(*) as count FROM orders WHERE status = 'Processing'", one=True)['count'],
        'Shipped': query_db("SELECT COUNT(*) as count FROM orders WHERE status = 'Shipped'", one=True)['count'],
        'Delivered': query_db("SELECT COUNT(*) as count FROM orders WHERE status = 'Delivered'", one=True)['count'],
        'Cancelled': query_db("SELECT COUNT(*) as count FROM orders WHERE status = 'Cancelled'", one=True)['count']
    }

    return render_template(
        'admin/orders.html',
        orders=orders_list,
        current_status=status_filter,
        status_counts=status_counts
    )


@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    """Updates order fulfillment status (Pending, Processing, Shipped, Delivered, Cancelled)."""
    new_status = request.form.get('status')
    valid_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']

    if new_status in valid_statuses:
        execute_db("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        flash(f'Order #{order_id} status updated to "{new_status}".', 'success')
    else:
        flash('Invalid status provided.', 'danger')

    return redirect(request.referrer or url_for('admin_orders'))


# -----------------------------------------------------------------------------
# ERROR HANDLERS
# -----------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', error_title="404 - Page Not Found",
                           error_msg="The page you requested could not be found."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('base.html', error_title="500 - Server Error",
                           error_msg="An internal server error occurred."), 500


if __name__ == '__main__':
    # Run development server on port 5000
    app.run(debug=True, host='127.0.0.1', port=5000)
