from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "rexglobal_secret_key"
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- ADMİN AYARLARI ---
ADMIN_USER = "Administrator" 
ADMIN_PASS = "adminrex" 
# ----------------------

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def db_query(query, params=(), one=False, commit=False):
    conn = sqlite3.connect(DB_PATH)
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

def init_db():
    if not os.path.exists(UPLOAD_FOLDER): 
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Kullanıcılar Tablosu
    db_query('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user')''', commit=True)
        
    # Ürünler Tablosu
    db_query('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL,
        img TEXT)''', commit=True)

    # KATEGORİLER TABLOSU (YENİ)
    db_query('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE)''', commit=True)
    
    # Admin Hesabı Kontrolü
    admin_check = db_query("SELECT * FROM users WHERE email = ?", (ADMIN_USER,), one=True)
    if not admin_check:
        db_query("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", 
                 (ADMIN_USER, ADMIN_PASS, "administrator"), commit=True)

with app.app_context():
    init_db()

# --- API ---
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
            return redirect(url_for('index'))
        else:
            return "Giriş Başarısız! Kullanıcı Adı Veya Şifre Hatalı.", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email != ADMIN_USER and "@" not in email:
            return "Hata: Geçerli Bir E-Posta Adresi Girmeniz Gerekmektedir!", 400
        try:
            db_query("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", 
                     (email, password, 'user'), commit=True)
            return redirect(url_for('login'))
        except:
            return "Bu Kullanıcı Adı Veya E-Posta Zaten Kayıtlı!", 400
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- ADMİN PANELİ VE KATEGORİ YÖNETİMİ ---
@app.route('/admin')
def admin_panel():
    if session.get('role') != 'administrator':
        return "Yetkisiz Erişim!", 403
    products = db_query("SELECT * FROM products")
    users = db_query("SELECT * FROM users")
    categories = db_query("SELECT * FROM categories") # Kategorileri çek
    return render_template('admin.html', products=products, users=users, categories=categories)

@app.route('/admin/add_category', methods=['POST'])
def add_category():
    if session.get('role') != 'administrator': return "Yetkisiz!", 403
    cat_name = request.form.get('category_name')
    if cat_name:
        try:
            db_query("INSERT INTO categories (name) VALUES (?)", (cat_name,), commit=True)
        except:
            pass
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_category/<int:id>')
def delete_category(id):
    if session.get('role') != 'administrator': return "Yetkisiz!", 403
    db_query("DELETE FROM categories WHERE id = ?", (id,), commit=True)
    return redirect(url_for('admin_panel'))

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if session.get('role') != 'administrator': return "Yetkisiz!", 403
    name = request.form.get('name')
    cat = request.form.get('category')
    price = request.form.get('price')
    file = request.files.get('img')
    img_path = "/static/uploads/no-image.png"
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_path = f"/static/uploads/{filename}"
    
    db_query("INSERT INTO products (name, category, price, img) VALUES (?, ?, ? , ?)", 
             (name, cat, price, img_path), commit=True)
    return redirect(url_for('admin_panel'))

# --- ANA SAYFA ---
@app.route('/')
def index():
    categories = db_query("SELECT * FROM categories") # Kategorileri menü için çek
    return render_template('index.html', categories=categories)

# --- CHECKOUT ---
@app.route('/checkout')
def checkout():
    return render_template('checkout.html', items=[], total=0)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
