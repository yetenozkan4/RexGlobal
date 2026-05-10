# SkinMarket — CS2 Item Mağazası

Flask ile yazılmış, Render üzerinde yayınlanabilen oyun item satış sitesi.

---

## 🚀 GitHub'a Yükleme

```bash
cd gamestore
git init
git add .
git commit -m "ilk commit"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/skinmarket.git
git push -u origin main
```

---

## ☁️ Render'da Yayınlama

1. [render.com](https://render.com) → **New > Web Service**
2. GitHub reponuzu bağlayın
3. Ayarlar otomatik gelir (`render.yaml` sayesinde)
4. **Deploy** butonuna tıklayın
5. Birkaç dakika sonra siteniz `https://skinmarket.onrender.com` adresinde yayında

### Manuel ayarlar (render.yaml kullanmak istemezseniz):
| Alan | Değer |
|------|-------|
| Environment | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |

---

## 🌐 Özel Domain Bağlama (Render)

1. Render dashboard → servisiniz → **Settings > Custom Domains**
2. Domaininizi ekleyin (örn: `skinmarket.com`)
3. Domain sağlayıcınızda CNAME kaydı oluşturun:
   - **CNAME** → `skinmarket.onrender.com`
4. SSL otomatik aktif olur

---

## 💻 Yerel Geliştirme

```bash
pip install -r requirements.txt
python app.py
# http://localhost:5000 adresinde açılır
```

---

## 📁 Dosya Yapısı

```
gamestore/
├── app.py              # Flask backend + item verileri
├── requirements.txt    # Python bağımlılıkları
├── render.yaml         # Render deployment config
├── .gitignore
└── templates/
    └── index.html      # Tüm site (HTML + CSS + JS)
```
