# PANDUAN DEPLOYMENT: Instrumen SJT + Google Sheets

Panduan ini akan membantu Anda menghubungkan aplikasi Streamlit ke Google Sheets (agar data aman) dan memasangnya di VPS (agar bisa diakses online).

---

## BAGIAN 1: MENGHUBUNGKAN KE GOOGLE SHEETS (Wajib)

Agar data responden tersimpan aman di Google Drive Anda, ikuti langkah ini:

### 1. Buat Google Cloud Service Account
1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Buat **Project Baru** (misal: `Disertasi-SJT`).
3. Cari dan aktifkan **"Google Sheets API"** dan **"Google Drive API"**.
4. Masuk ke menu **Credentials** > **Create Credentials** > **Service Account**.
5. Beri nama, klik Done.
6. Klik email service account yang baru dibuat (ujungnya `@...iam.gserviceaccount.com`), masuk ke tab **Keys**.
7. **Add Key** > **Create New Key** > **JSON**.
8. File JSON akan terdownload ke komputer Anda. **Simpan file ini!**

### 2. Siapkan Google Sheet
1. Buat Spreadsheet baru di Google Sheets Anda (misal: `Data_Responden_Disertasi`).
2. **Share (Bagikan)** spreadsheet tersebut ke **email service account** tadi (email yang ada di file JSON). Beri akses sebagai **Editor**.
3. Salin URL spreadsheet tersebut.

### 3. Konfigurasi di Aplikasi
1. Buat folder bernama `.streamlit` di dalam folder `web_sjt`.
2. Di dalamnya, buat file bernama `secrets.toml`.
3. Isi file `secrets.toml` dengan format berikut (copy isi file JSON Anda):

```toml
[spreadsheet]
url = "PASTE_URL_SPREADSHEET_DISINI"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "..."
token_uri = "..."
auth_provider_x509_cert_url = "..."
client_x509_cert_url = "..."
```

*(Isi bagian `...` dengan menyalin persis dari file JSON yang Anda download).*

---

## BAGIAN 2: UPLOAD KE VPS (Agar Online)

Jika Anda menyewa VPS (misal: DigitalOcean/IDCloudHost dengan OS Ubuntu), ikuti langkah ini:

### 1. Upload File
Gunakan aplikasi **FileZilla**.
- Host: IP VPS Anda
- User: root
- Pass: password vps
- Upload seluruh isi folder `web_sjt` ke folder `/root/web_sjt` di server.
- **PENTING:** Jangan lupa upload juga folder `.streamlit` yang berisi `secrets.toml` tadi agar koneksi database jalan.

### 2. Jalankan Perintah Instalasi
Buka terminal (SSH) ke VPS Anda, lalu ketik:

```bash
cd /root/web_sjt
bash deploy_vps.sh
```

Tunggu proses selesai. Jika sukses, aplikasi akan langsung bisa dibuka dengan mengetik IP VPS Anda di browser (tanpa port).

---

## OPSI ALTERNATIF: Streamlit Community Cloud (GRATIS)

Jika VPS terlalu rumit, gunakan cara gratis ini:
1. Upload folder `web_sjt` ke **GitHub** pribadi Anda.
2. Buka [share.streamlit.io](https://share.streamlit.io).
3. Login dengan GitHub, klik **New App**.
4. Pilih repo GitHub Anda, dan file utamanya `app_sjt_gsheets.py`.
5. Sebelum klik Deploy, klik **Advanced Settings** > **Secrets**.
6. Copy-paste isi `secrets.toml` ke kotak Secrets tersebut.
7. Klik **Deploy**.

Selesai! Anda punya link survei online gratis (misal: `disertasi-anda.streamlit.app`).
