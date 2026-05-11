from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "rexglobal_secret_key"
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Veritabanı Bağlantı Yardımcısı (Kod tekrarını engeller)
def db_query(query, params=(), one=False, commit=False):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.execute(query, params)
    if commit:
        conn.commit()
        res = cur.lastrowid
    else:
        res = cur.fetchone() if one else cur.fetchall()
    conn.close()
    return res

# Tabloları Hazırla
def init_db():
    if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
    db_query('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user')''', commit=True)
    db_query('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL,
        discount_price REAL,
        discount_end DATETIME,
        img TEXT)''', commit=True)

# --- AUTH SİSTEMİ ---
@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        db_query("INSERT INTO users (email, password) VALUES (?, ?)", (email, password), commit=True)
        return redirect(url_for('login_page'))
    except: return "Bu e-posta zaten kayıtlı!", 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db_query("SELECT * FROM users WHERE email = ? AND password = ?", (email, password), one=True)
        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['role'] = user['role']
            # ÖZEL KURAL: Belirttiğin mail otomatik admin olur
            if email == "admin@rexglobal.com" and password == "admin123":
                db_query("UPDATE users SET role = 'administrator' WHERE email = ?", (email,), commit=True)
                session['role'] = 'administrator'
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- ADMİN PANELİ ---
@app.route('/admin')
def admin_panel():
    if session.get('role') != 'administrator':
        return "Yetkisiz Erişim!", 403
    products = db_query("SELECT * FROM products")
    users = db_query("SELECT * FROM users")
    return render_template('admin.html', products=products, users=users)

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    name = request.form.get('name')
    cat = request.form.get('category')
    price = request.form.get('price')
    file = request.files.get('img')
    img_path = ""
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_path = f"/static/uploads/{filename}"
    
    db_query("INSERT INTO products (name, category, price, img) VALUES (?, ?, ?, ?)", 
             (name, cat, price, img_path), commit=True)
    return redirect(url_for('admin_panel'))

@app.route('/admin/set_discount/<int:id>', methods=['POST'])
def set_discount(id):
    d_price = request.form.get('discount_price')
    d_end = request.form.get('discount_end') # Format: 2026-05-20T18:00
    db_query("UPDATE products SET discount_price = ?, discount_end = ? WHERE id = ?", 
             (d_price, d_end, id), commit=True)
    return redirect(url_for('admin_panel'))

# --- SEPET & ÖDEME ---
@app.route('/cart/add/<int:id>')
def add_to_cart(id):
    cart = session.get('cart', [])
    cart.append(id)
    session['cart'] = cart
    return redirect(url_for('index'))

@app.route('/checkout')
def checkout():
    if 'user_id' not in session: return redirect(url_for('login'))
    # Sepetteki ürünleri çek
    cart_ids = session.get('cart', [])
    items = []
    total = 0
    for cid in cart_ids:
        p = db_query("SELECT * FROM products WHERE id = ?", (cid,), one=True)
        if p: 
            items.append(p)
            total += p['discount_price'] if p['discount_price'] else p['price']
    return render_template('checkout.html', items=items, total=total)

@app.route('/')
def index():
    # Session verilerini çekip HTML'e gönderiyoruz
    products = db_query("SELECT * FROM products")
    return render_template('index.html', products=products, session=session)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
