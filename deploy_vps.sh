#!/bin/bash

# Skrip Deployment Otomatis untuk VPS Ubuntu 22.04/24.04
# Jalankan dengan: bash deploy_vps.sh

echo "=== MEMULAI INSTALASI STREAMLIT SERVER ==="

# 1. Update System
echo "[1/5] Mengupdate sistem..."
sudo apt-get update

# 2. Instal Python & Venv
echo "[2/5] Menginstal Python..."
sudo apt-get install -y python3-pip python3-venv

# 3. Buat Virtual Environment
echo "[3/5] Membuat Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

# 4. Instal Library
echo "[4/5] Menginstal Library Python..."
pip install -r requirements.txt

# 5. Menjalankan Aplikasi di Background
echo "[5/5] Menjalankan Aplikasi..."
# Matikan proses streamlit yang lama jika ada
pkill -f streamlit

# Jalankan baru dengan nohup (agar tetap jalan saat terminal ditutup)
nohup streamlit run app_sjt_gsheets.py --server.port 80 --server.address 0.0.0.0 > app.log 2>&1 &

echo "=== SELESAI! ==="
echo "Aplikasi Anda sekarang berjalan di IP Server ini."
echo "Cek log jika ada error: cat app.log"
