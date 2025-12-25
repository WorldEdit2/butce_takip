import sqlite3
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Veritabanı Yolu (Volume ile kalıcı olacak)
DB_FOLDER = '/app/data'
DB_FILE = os.path.join(DB_FOLDER, 'budget.db')

def init_db():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Tarih, Kategori, Tutar, Aciklama
    c.execute('''CREATE TABLE IF NOT EXISTS expenses 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  category TEXT, amount REAL, description TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- WEB ARAYÜZÜ ---
@app.route('/')
def index():
    return render_template('index.html')

# --- API ENDPOINTLERİ ---

# 1. Yeni Harcama Ekle (POST)
@app.route('/api/add', methods=['POST'])
def add_expense():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Veri yok"}), 400
        
    category = data.get('category')
    amount = data.get('amount')
    description = data.get('description', '')

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO expenses (category, amount, description) VALUES (?, ?, ?)", 
              (category, amount, description))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Harcama eklendi!", "data": data}), 201

# 2. İstatistikleri Getir (GET) - Grafikler için
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Kategorilere göre toplam tutarı hesapla (SQL Gücü)
    c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    rows = c.fetchall()
    conn.close()
    
    # Chart.js'in anlayacağı format: {labels: [], values: []}
    stats = {
        "labels": [row[0] for row in rows],
        "values": [row[1] for row in rows]
    }
    return jsonify(stats)

# 3. Son Harcamaları Listele
@app.route('/api/list', methods=['GET'])
def get_list():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT category, amount, description FROM expenses ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    
    transactions = [{"category": r[0], "amount": r[1], "desc": r[2]} for r in rows]
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
