import sqlite3
import os

# app.py'nin olduğu tam klasör yolunu bulur
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'database.db')

def get_db_connection():
    # Bu fonksiyon her çağrıldığında veritabanına bağlanır
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "rex_gizli_anahtar"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Başlangıç ürünleri (Burayı istediğin gibi çoğaltabilirsin)
ITEMS = [
    {"id": 1, "name": "AK-47 | Redline", "game": "Counter-Strike 2", "category": "Silah Kını", "price": 18.50, "rarity": "Classified", "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEj5VHCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 0, "wear": "Field-Tested", "float": 0.23}
]

ADMIN_PASS = "admin123"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    is_admin = session.get("is_admin", False)
    # RENDER İÇİN: templates klasöründeki dosya adıyla BİREBİR AYNI olmalı (küçük harf!)
    return render_template("index.html", is_admin=is_admin)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASS:
            session["is_admin"] = True
            return redirect(url_for("admin_panel")) # Giriş yapınca Admin Panele git
    return render_template("login.html")

# EKSİK OLAN VE 404 VERDİREN KISIM BURASIYDI:
@app.route("/admin")
def admin_panel():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    return render_template("admin.html")

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))

@app.route("/admin/add", methods=["POST"])
def add_item():
    if not session.get("is_admin"):
        return "Yetkisiz Erişim", 403
    
    file = request.files.get('item_img')
    img_url = ""
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Render'da static/uploads klasörü yoksa hata verebilir, o yüzden kontrol ekledik
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_url = f"/static/uploads/{filename}"

    new_item = {
        "id": len(ITEMS) + 1,
        "name": request.form.get("name"),
        "game": "Counter-Strike 2",
        "category": request.form.get("category"),
        "price": float(request.form.get("price")),
        "rarity": request.form.get("rarity"),
        "img": img_url,
        "discount": int(request.form.get("discount") or 0),
        "wear": request.form.get("wear"),
        "float": float(request.form.get("float") or 0)
    }
    ITEMS.append(new_item)
    return redirect(url_for("index"))

@app.route("/api/items")
def get_items():
    category = request.args.get("category", "all")
    rarity = request.args.get("rarity", "all")
    q = request.args.get("q", "").lower()
    
    result = ITEMS[:]
    if category != "all":
        result = [i for i in result if i["category"] == category]
    if rarity != "all":
        result = [i for i in result if i["rarity"] == rarity]
    if q:
        result = [i for i in result if q in i["name"].lower()]
    
    return jsonify(result)

if __name__ == "__main__":
   if __name__ == "__main__":
    # Site açılmadan önce veritabanı tablosu yoksa oluşturur
    conn = get_db_connection()
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
            float REAL
        )
    ''')
    conn.commit()
    conn.close()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    # Render portu buradan otomatik alır
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
