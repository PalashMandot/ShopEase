"""
test_portal.py - Comprehensive Unit & Integration Test Suite for ShopEase.
Validates all 10 TA-2 Evaluation requirements:
1. Register customer
2. Log in
3. Browse & search products
4. Add to cart
5. Change quantities
6. Complete checkout
7. Verify saved order & order history
8. Log in as administrator
9. Add product & update inventory
10. Update order status
"""

import unittest
from app import app
from database import query_db, execute_db, init_db, seed_data


class ShopEaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        # Reset and seed database
        init_db()
        seed_data()
        execute_db("DELETE FROM cart_items")
        execute_db("DELETE FROM order_items")
        execute_db("DELETE FROM orders")

    # 1. Register a new customer
    def test_01_customer_registration(self):
        response = self.client.post('/register', data={
            'name': 'Anita Desai',
            'email': 'anita@test.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'phone': '+91 9988776655',
            'address': '123 Palm Grove Road, Indiranagar, Bengaluru'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        user = query_db("SELECT * FROM users WHERE email = 'anita@test.com'", one=True)
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], 'Anita Desai')
        self.assertEqual(user['is_admin'], 0)
        print("[PASS] Step 1: Customer registered successfully.")

    # 2. Customer Log in
    def test_02_customer_login(self):
        response = self.client.post('/login', data={
            'email': 'user@shopease.com',
            'password': 'user123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertIn('user_id', sess)
            self.assertEqual(sess['user_email'], 'user@shopease.com')
            self.assertFalse(sess['is_admin'])
        print("[PASS] Step 2: Customer logged in successfully.")

    # 3. Browse and Search Products
    def test_03_browse_and_search_products(self):
        # Browse catalog
        res_catalog = self.client.get('/products')
        self.assertEqual(res_catalog.status_code, 200)
        self.assertIn(b'Noise-Cancelling Wireless Headphones', res_catalog.data)

        # Search by keyword
        res_search = self.client.get('/products?q=Watch')
        self.assertEqual(res_search.status_code, 200)
        self.assertIn(b'Ultra HD Smart Watch Pro', res_search.data)

        # Filter by category
        res_cat = self.client.get('/products?category=1')
        self.assertEqual(res_cat.status_code, 200)
        print("[PASS] Step 3: Browse and search products functional.")

    # 4. Add products to cart
    def test_04_add_to_cart(self):
        # Login customer first
        self.client.post('/login', data={'email': 'user@shopease.com', 'password': 'user123'})

        # Find product
        prod = query_db("SELECT id, name, price FROM products LIMIT 1", one=True)
        res_add = self.client.post(f'/cart/add/{prod["id"]}', data={'quantity': 2}, follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)

        # Check cart
        cart_row = query_db(
            "SELECT * FROM cart_items WHERE product_id = ?", (prod['id'],), one=True
        )
        self.assertIsNotNone(cart_row)
        self.assertEqual(cart_row['quantity'], 2)
        print("[PASS] Step 4: Product added to cart successfully.")

    # 5. Change quantities in cart
    def test_05_update_cart_quantity(self):
        self.client.post('/login', data={'email': 'user@shopease.com', 'password': 'user123'})
        prod = query_db("SELECT id FROM products LIMIT 1", one=True)
        self.client.post(f'/cart/add/{prod["id"]}', data={'quantity': 1})

        # Update to 3
        res_upd = self.client.post(f'/cart/update/{prod["id"]}', data={'quantity': 3}, follow_redirects=True)
        self.assertEqual(res_upd.status_code, 200)

        cart_row = query_db("SELECT quantity FROM cart_items WHERE product_id = ?", (prod['id'],), one=True)
        self.assertEqual(cart_row['quantity'], 3)
        print("[PASS] Step 5: Cart quantity updated successfully.")

    # 6 & 7. Complete Checkout and Verify Order in History
    def test_06_and_07_checkout_and_order_history(self):
        self.client.post('/login', data={'email': 'user@shopease.com', 'password': 'user123'})

        # Add item to cart
        prod = query_db("SELECT id, stock FROM products WHERE stock >= 2 LIMIT 1", one=True)
        initial_stock = prod['stock']
        self.client.post(f'/cart/add/{prod["id"]}', data={'quantity': 2})

        # Place Order via COD
        res_order = self.client.post('/checkout/place-order', data={
            'customer_name': 'Rahul Sharma',
            'customer_phone': '+91 9876543211',
            'shipping_address': 'Flat 402, Green Glen Layout, Bellandur',
            'city': 'Bengaluru',
            'postal_code': '560103',
            'order_notes': 'Please ring the doorbell twice',
            'payment_method': 'Cash on Delivery'
        }, follow_redirects=True)

        self.assertEqual(res_order.status_code, 200)
        self.assertIn(b'Thank You for Your Order', res_order.data)

        # Verify order in database
        order = query_db("SELECT * FROM orders ORDER BY id DESC LIMIT 1", one=True)
        self.assertIsNotNone(order)
        self.assertEqual(order['payment_method'], 'Cash on Delivery')
        self.assertEqual(order['status'], 'Pending')

        # Verify stock decrement
        updated_prod = query_db("SELECT stock FROM products WHERE id = ?", (prod['id'],), one=True)
        self.assertEqual(updated_prod['stock'], initial_stock - 2)

        # Verify order history page
        res_history = self.client.get('/orders')
        self.assertIn(order['order_number'].encode(), res_history.data)
        print("[PASS] Steps 6 & 7: Checkout placed order, stock decremented, and visible in order history.")

    # 8. Admin Login & Access Control
    def test_08_admin_login(self):
        res = self.client.post('/login', data={
            'email': 'admin@shopease.com',
            'password': 'admin123'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertTrue(sess.get('is_admin'))

        # Check admin dashboard access
        res_dash = self.client.get('/admin')
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn(b'Dashboard Overview', res_dash.data)
        print("[PASS] Step 8: Admin authenticated and dashboard rendered.")

    # 9. Add product and update inventory
    def test_09_admin_add_and_update_product(self):
        execute_db("DELETE FROM products WHERE name = 'Wireless Ergonomic Vertical Mouse'")
        self.client.post('/login', data={'email': 'admin@shopease.com', 'password': 'admin123'})

        # Add Product
        res_add = self.client.post('/admin/products/add', data={
            'name': 'Wireless Ergonomic Vertical Mouse',
            'category_id': 1,
            'description': 'High precision optical sensor with rechargeable battery and silent click buttons.',
            'price': '1499.00',
            'stock': '40',
            'image_url': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=80',
            'featured': '1'
        }, follow_redirects=True)

        self.assertEqual(res_add.status_code, 200)

        new_prod = query_db("SELECT * FROM products WHERE name = 'Wireless Ergonomic Vertical Mouse'", one=True)
        self.assertIsNotNone(new_prod)
        self.assertEqual(new_prod['stock'], 40)

        # Update Stock
        res_stock = self.client.post(f'/admin/products/update-stock/{new_prod["id"]}', data={'stock': 75}, follow_redirects=True)
        self.assertEqual(res_stock.status_code, 200)
        rechecked = query_db("SELECT stock FROM products WHERE id = ?", (new_prod['id'],), one=True)
        self.assertEqual(rechecked['stock'], 75)
        print("[PASS] Step 9: Admin added product and updated inventory stock.")

    # 10. Update Order Status
    def test_10_admin_update_order_status(self):
        # Create a dummy order
        user = query_db("SELECT id FROM users WHERE is_admin = 0 LIMIT 1", one=True)
        order_id = execute_db('''
            INSERT INTO orders (
                order_number, user_id, customer_name, customer_email, customer_phone,
                shipping_address, city, postal_code, subtotal, shipping_fee, total_amount, status
            ) VALUES ('SE-TEST-9999', ?, 'Test Customer', 'test@test.com', '9876543210',
                      'Test Address', 'Bengaluru', '560001', 1999.0, 0.0, 1999.0, 'Pending')
        ''', (user['id'],))

        self.client.post('/login', data={'email': 'admin@shopease.com', 'password': 'admin123'})

        # Update status to Shipped
        res_upd = self.client.post(f'/admin/orders/{order_id}/status', data={'status': 'Shipped'}, follow_redirects=True)
        self.assertEqual(res_upd.status_code, 200)

        order = query_db("SELECT status FROM orders WHERE id = ?", (order_id,), one=True)
        self.assertEqual(order['status'], 'Shipped')
        print("[PASS] Step 10: Admin updated order status from Pending to Shipped.")


if __name__ == '__main__':
    unittest.main()
