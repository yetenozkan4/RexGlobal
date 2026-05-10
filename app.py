from flask import Flask, render_template, jsonify, request
import os

app = Flask(__name__)

ITEMS = [
    {"id": 1,  "name": "AK-47 | Redline",        "game": "Counter-Strike 2",  "category": "Silah Kını",   "price": 18.50, "rarity": "Classified",  "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEj5VHCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 0,  "wear": "Field-Tested",     "float": 0.23},
    {"id": 2,  "name": "AWP | Dragon Lore",       "game": "Counter-Strike 2",  "category": "Silah Kını",   "price": 1850.00,"rarity": "Covert",     "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEjAXHRuCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 5,  "wear": "Factory New",     "float": 0.01},
    {"id": 3,  "name": "M4A4 | Howl",             "game": "Counter-Strike 2",  "category": "Silah Kını",   "price": 2400.00,"rarity": "Contraband", "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEjAXHRuCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 0,  "wear": "Minimal Wear",    "float": 0.08},
    {"id": 4,  "name": "Butterfly Knife | Fade",  "game": "Counter-Strike 2",  "category": "Bıçak",       "price": 620.00, "rarity": "Covert",     "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEjEXHRuCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 10, "wear": "Factory New",     "float": 0.02},
    {"id": 5,  "name": "Bayonet | Tiger Tooth",   "game": "Counter-Strike 2",  "category": "Bıçak",       "price": 290.00, "rarity": "Covert",     "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEjEXHRuCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 0,  "wear": "Factory New",     "float": 0.00},
    {"id": 6,  "name": "Glock-18 | Fade",         "game": "Counter-Strike 2",  "category": "Silah Kını",   "price": 340.00, "rarity": "Restricted", "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEjAXHRuCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 0,  "wear": "Factory New",     "float": 0.01},
    {"id": 7,  "name": "Karambit | Doppler",      "game": "Counter-Strike 2",  "category": "Bıçak",       "price": 780.00, "rarity": "Covert",     "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEjEXHRuCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 8,  "wear": "Factory New",     "float": 0.01},
    {"id": 8,  "name": "Desert Eagle | Blaze",    "game": "Counter-Strike 2",  "category": "Silah Kını",   "price": 95.00,  "rarity": "Restricted", "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEjAXHRuCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 0,  "wear": "Factory New",     "float": 0.02},
    {"id": 9,  "name": "StatTrak AK-47 | Fire Serpent","game": "Counter-Strike 2","category": "Silah Kını","price": 850.00, "rarity": "Covert",   "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEjAXHRuCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 0,  "wear": "Minimal Wear",    "float": 0.12},
    {"id": 10, "name": "M9 Bayonet | Marble Fade","game": "Counter-Strike 2",  "category": "Bıçak",       "price": 420.00, "rarity": "Covert",     "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEjEXHRuCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 15, "wear": "Factory New",     "float": 0.01},
    {"id": 11, "name": "USP-S | Kill Confirmed",  "game": "Counter-Strike 2",  "category": "Silah Kını",   "price": 42.00,  "rarity": "Covert",     "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEjAXHRuCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 0,  "wear": "Field-Tested",    "float": 0.21},
    {"id": 12, "name": "Flip Knife | Crimson Web", "game": "Counter-Strike 2", "category": "Bıçak",       "price": 175.00, "rarity": "Covert",     "img": "https://community.cloudflare.steamstatic.com/economy/image/fWFc82js0fmoRAP-qOIPu5THSWqfSmTELLqcUywGkijVjZULUrsm1j-9xgEPaQNMWZ8M3UFBOcpEjEXHRuCbknuQf-oJGplXNB4TKaPfYgCIBEYAivqFeOfepHMuDn0B4RdA", "discount": 0,  "wear": "Field-Tested",    "float": 0.27},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/items")
def get_items():
    category = request.args.get("category", "all")
    rarity   = request.args.get("rarity", "all")
    sort     = request.args.get("sort", "default")
    q        = request.args.get("q", "").lower()
    result = ITEMS[:]
    if category != "all":
        result = [i for i in result if i["category"] == category]
    if rarity != "all":
        result = [i for i in result if i["rarity"] == rarity]
    if q:
        result = [i for i in result if q in i["name"].lower()]
    if sort == "price_asc":
        result.sort(key=lambda x: x["price"])
    elif sort == "price_desc":
        result.sort(key=lambda x: x["price"], reverse=True)
    elif sort == "discount":
        result.sort(key=lambda x: x["discount"], reverse=True)
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
