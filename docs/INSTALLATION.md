# Panduan Instalasi Server SeKuNe

Dokumen ini menjelaskan langkah-langkah instalasi aplikasi SeKuNe dari awal hingga siap digunakan.

## 📋 Persyaratan Sistem

### Minimum Requirements
- **Operating System**: Ubuntu 18.04+ / Windows 10+ / macOS 10.14+
- **Python**: 3.8 atau lebih baru
- **Node.js**: 16.0 atau lebih baru
- **npm/pnpm**: Package manager untuk Node.js
- **RAM**: Minimum 2GB
- **Storage**: Minimum 1GB ruang kosong
- **Network**: Koneksi internet untuk download dependencies

### Recommended Requirements
- **Operating System**: Ubuntu 20.04+ / Windows 11 / macOS 12+
- **Python**: 3.11+
- **Node.js**: 18.0+
- **RAM**: 4GB atau lebih
- **Storage**: 5GB atau lebih ruang kosong

## 🔧 Instalasi Dependencies

### 1. Install Python
#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Windows:
1. Download Python dari https://python.org/downloads/
2. Jalankan installer dan centang "Add Python to PATH"
3. Verifikasi instalasi: `python --version`

#### macOS:
```bash
# Menggunakan Homebrew
brew install python3
```

### 2. Install Node.js
#### Ubuntu/Debian:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### Windows:
1. Download Node.js dari https://nodejs.org/
2. Jalankan installer
3. Verifikasi instalasi: `node --version`

#### macOS:
```bash
# Menggunakan Homebrew
brew install node
```

### 3. Install pnpm (Opsional, tapi direkomendasikan)
```bash
npm install -g pnpm
```

## 📥 Download dan Setup Aplikasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd sekune
```

### 2. Setup Backend

#### Masuk ke direktori backend:
```bash
cd sekune_backend
```

#### Buat virtual environment:
```bash
python3 -m venv venv
```

#### Aktifkan virtual environment:
**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

#### Install dependencies Python:
```bash
pip install -r requirements.txt
```

#### Setup database (otomatis saat pertama kali dijalankan):
```bash
python src/main.py
```

### 3. Setup Frontend

#### Buka terminal baru dan masuk ke direktori frontend:
```bash
cd sekune_frontend
```

#### Install dependencies Node.js:
```bash
# Menggunakan npm
npm install

# Atau menggunakan pnpm (direkomendasikan)
pnpm install
```

## 🚀 Menjalankan Aplikasi

### 1. Jalankan Backend Server

#### Masuk ke direktori backend dan aktifkan virtual environment:
```bash
cd sekune_backend
source venv/bin/activate  # Linux/macOS
# atau
venv\Scripts\activate     # Windows
```

#### Jalankan server:
```bash
python src/main.py
```

Server backend akan berjalan di: **http://localhost:5000**

### 2. Jalankan Frontend Development Server

#### Buka terminal baru dan masuk ke direktori frontend:
```bash
cd sekune_frontend
```

#### Jalankan development server:
```bash
# Menggunakan npm
npm run dev

# Atau menggunakan pnpm
pnpm run dev
```

Frontend akan berjalan di: **http://localhost:5173**

## 🔐 Akun Default

Setelah instalasi berhasil, gunakan akun berikut untuk login pertama kali:

**Administrator:**
- Email: `admin@sekune.com`
- Password: `admin123`

## 🌐 Akses Aplikasi

1. Buka browser web
2. Kunjungi: **http://localhost:5173**
3. Login menggunakan akun administrator default
4. Mulai konfigurasi sistem sesuai kebutuhan sekolah

## 🏭 Deployment Production

### 1. Build Frontend untuk Production
```bash
cd sekune_frontend
npm run build
# atau
pnpm run build
```

### 2. Copy Build ke Backend Static Directory
```bash
cp -r dist/* ../sekune_backend/src/static/
```

### 3. Setup Production Environment

#### Install production dependencies:
```bash
cd sekune_backend
pip install gunicorn
```

#### Jalankan dengan Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

### 4. Setup Reverse Proxy (Nginx)

#### Install Nginx:
```bash
sudo apt install nginx
```

#### Konfigurasi Nginx (`/etc/nginx/sites-available/sekune`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Aktifkan konfigurasi:
```bash
sudo ln -s /etc/nginx/sites-available/sekune /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Konfigurasi Environment Variables

Buat file `.env` di direktori `sekune_backend`:

```env
# Database Configuration
DATABASE_URL=sqlite:///sekune.db
# Untuk production dengan PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost/sekune_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,https://your-domain.com
```

## 🗄 Database Setup (PostgreSQL untuk Production)

### 1. Install PostgreSQL:
```bash
sudo apt install postgresql postgresql-contrib
```

### 2. Setup Database:
```bash
sudo -u postgres psql
CREATE DATABASE sekune_db;
CREATE USER sekune_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sekune_db TO sekune_user;
\q
```

### 3. Update Environment Variables:
```env
DATABASE_URL=postgresql://sekune_user:your_password@localhost/sekune_db
```

## 🔒 Security Considerations

### 1. Firewall Configuration:
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2. SSL Certificate (Let's Encrypt):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Regular Updates:
```bash
# Update sistem
sudo apt update && sudo apt upgrade

# Update Python packages
pip install --upgrade -r requirements.txt

# Update Node.js packages
npm update
```

## 🐛 Troubleshooting

### Port sudah digunakan:
```bash
# Cek proses yang menggunakan port
sudo lsof -i :5000
sudo lsof -i :5173

# Kill proses jika diperlukan
sudo kill -9 <PID>
```

### Permission denied:
```bash
# Fix permission untuk direktori
sudo chown -R $USER:$USER /path/to/sekune
chmod -R 755 /path/to/sekune
```

### Database connection error:
1. Pastikan database service berjalan
2. Cek konfigurasi DATABASE_URL
3. Pastikan user database memiliki permission yang tepat

### Frontend tidak bisa connect ke backend:
1. Pastikan backend berjalan di port 5000
2. Cek konfigurasi CORS di backend
3. Pastikan tidak ada firewall yang memblokir koneksi

## 📞 Support

Jika mengalami masalah selama instalasi:
1. Cek log error di terminal
2. Pastikan semua dependencies terinstall dengan benar
3. Verifikasi konfigurasi environment variables
4. Buat issue di repository GitHub dengan detail error

---

**Selamat! Aplikasi SeKuNe siap digunakan.** 🎉

