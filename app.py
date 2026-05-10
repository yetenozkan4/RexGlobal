from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "rex_gizli_anahtar"

# Veritabanı ve Klasör Yolları
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'database.db')
UPLOAD_FOLDER = os.path.join(base_dir, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Veritabanı Bağlantısı
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Veritabanını ve Tabloları Başlat (Rol Sistemi Dahil)
def init_db():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    conn = get_db_connection()
    # Ürünler Tablosu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            game TEXT,
            category TEXT,
            price REAL,
            rarity TEXT,
            img TEXT,
            wear TEXT,
            float REAL,
            discount INTEGER DEFAULT 0
        )
    ''')
    # Kullanıcılar ve Roller Tablosu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user' -- 'admin' veya 'user'
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/")
def index():
    is_admin = session.get("is_admin", False)
    return render_template("index.html", is_admin=is_admin)

# --- ÜRÜN YÖNETİMİ (SİLME DAHİL) ---

@app.route("/api/items")
def get_items():
    category = request.args.get("category", "all")
    rarity = request.args.get("rarity", "all")
    q = request.args.get("q", "").lower()
    
    conn = get_db_connection()
    query = "SELECT * FROM items WHERE 1=1"
    params = []
    
    if category != "all":
        query += " AND category = ?"
        params.append(category)
    if rarity != "all":
        query += " AND rarity = ?"
        params.append(rarity)
    if q:
        query += " AND LOWER(name) LIKE ?"
        params.append(f'%{q}%')
        
    items = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in items])

@app.route("/admin/delete/<int:id>", methods=["POST"])
def delete_item(id):
    if not session.get("is_admin"):
        return "Yetkisiz Erişim", 403
    
    conn = get_db_connection()
    conn.execute("DELETE FROM items WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_panel"))

# --- YÖNETİM PANELİ VE ROL SİSTEMİ ---

@app.route("/admin")
def admin_panel():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    
    try:
        conn = get_db_connection()
        # Ürünleri ve kullanıcıları çekiyoruz
        items_db = conn.execute("SELECT * FROM items").fetchall()
        users_db = conn.execute("SELECT * FROM users").fetchall()
        conn.close()
        
        # Veritabanından gelen verileri listeye çeviriyoruz
        items = [dict(ix) for ix in items_db]
        users = [dict(ux) for ux in users_db]
        
    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        items = [] # Hata olursa sayfa çökmesin diye boş liste yolluyoruz
        users = []

    # HTML'e gönderdiğimiz değişken isimleri (items ve users) admin.html ile aynı olmalı
    return render_template("admin.html", items=items, users=users)
    
    conn = get_db_connection()
    # Veritabanından ürünleri ve kullanıcıları çekiyoruz
    items = conn.execute("SELECT * FROM items").fetchall()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    
    # BURASI ÇOK ÖNEMLİ: items ve users değişkenlerini HTML'e gönderiyoruz
    return render_template("admin.html", items=items, users=users)
    
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM items").fetchall()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return render_template("admin.html", items=items, users=users)

@app.route("/admin/update_role/<int:user_id>", methods=["POST"])
def update_role(user_id):
    if not session.get("is_admin"): return "Hata", 403
    new_role = request.form.get("role")
    
    conn = get_db_connection()
    conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_panel"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Şimdilik basit şifre, ileride DB'den kullanıcı kontrolü yapılabilir
        if request.form.get("password") == "admin123":
            session["is_admin"] = True
            return redirect(url_for("admin_panel"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# --- ÜRÜN EKLEME ---
@app.route("/admin/add", methods=["POST"])
def add_item():
    if not session.get("is_admin"): return "Hata", 403
    
    # Formdan verileri alırken varsayılan değerler atıyoruz
    name = request.form.get("name")
    price = request.form.get("price", 0)
    category = request.form.get("category")
    rarity = request.form.get("rarity")
    wear = request.form.get("wear", "")
    # Float boş gelirse 0.0 yap (Çökmesini engeller)
    try:
        float_val = float(request.form.get("float") or 0)
    except:
        float_val = 0.0

    file = request.files.get('item_img')
    img_url = ""
    if file:
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_url = f"/static/uploads/{filename}"

    conn = get_db_connection()
    conn.execute('''INSERT INTO items 
        (name, game, category, price, rarity, img, wear, float) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (name, "Counter-Strike 2", category, price, rarity, img_url, wear, float_val))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_panel"))
    
    file = request.files.get('item_img')
    img_url = ""
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_url = f"/static/uploads/{filename}"

    conn = get_db_connection()
    conn.execute('''INSERT INTO items 
        (name, game, category, price, rarity, img, wear, float, discount) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (request.form.get("name"), "Counter-Strike 2", request.form.get("category"),
         float(request.form.get("price")), request.form.get("rarity"), img_url,
         request.form.get("wear"), float(request.form.get("float") or 0), 0))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_panel"))

if __name__ == "__main__":
    init_db()  # <-- BU SATIR ÇOK KRİTİK!
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
