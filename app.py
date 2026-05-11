from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "rexglobal_secret_key"
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Veritabanı Bağlantı Yardımcısı
def db_query(query, params=(), one=False, commit=False):
    # Veritabanı yolu Render için tam yol olarak belirtildi
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(query, params)
        if commit:
            conn.commit()
            res = cur.lastrowid
        else:
            res = cur.fetchone() if one else cur.fetchall()
    finally:
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

# --- API (JS İÇİN GEREKLİ) ---
@app.route('/api/items')
def get_items():
    category = request.args.get('category', 'all')
    search = request.args.get('q', '').lower()
    
    if category == 'all':
        rows = db_query("SELECT * FROM products")
    else:
        rows = db_query("SELECT * FROM products WHERE category = ?", (category,))
    
    items = []
    for row in rows:
        if search in row['name'].lower():
            items.append({
                "id": row['id'],
                "name": row['name'],
                "price": row['price'],
                "img": row['img'],
                "category": row['category']
            })
    return jsonify(items)

# --- AUTH SİSTEMİ ---
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

# --- ANA SAYFA ---
@app.route('/')
def index():
    products = db_query("SELECT * FROM products")
    return render_template('index.html', products=products)

# --- RENDER UYUMLU ÇALIŞTIRICI ---
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
