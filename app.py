from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "rexglobal_secret_key"
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Veritabanı yolu Render için tam yol olarak belirtildi
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# Veritabanı Bağlantı Yardımcısı
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

# Tabloları Hazırla (Artık her uygulama başladığında otomatik kontrol edecek)
def init_db():
    if not os.path.exists(UPLOAD_FOLDER): 
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
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
    
    # İlk Admin Hesabını Otomatik Oluştur (Eğer yoksa)
    admin_check = db_query("SELECT * FROM users WHERE email = ?", ("admin@rexglobal.com",), one=True)
    if not admin_check:
        db_query("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", 
                 ("admin@rexglobal.com", "admin123", "administrator"), commit=True)

# UYGULAMA BAŞLATILDIĞINDA DB'Yİ KUR
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
            return "Giriş Başarısız! Email veya Şifre hatalı.", 401
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
    
    db_query("INSERT INTO products (name, category, price, img) VALUES (?, ?, ?, ?)", 
             (name, cat, price, img_path), commit=True)
    return redirect(url_for('admin_panel'))

# --- CHECKOUT (Log hatasını çözen rota) ---
@app.route('/checkout')
def checkout():
    # Şimdilik sepet boş gibi davranır veya login zorunluluğu koyabilirsin
    return render_template('checkout.html', items=[], total=0)

# --- ANA SAYFA ---
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
