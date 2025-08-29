# Troubleshooting Guide SeKuNe

Panduan mengatasi masalah umum yang mungkin terjadi saat menggunakan aplikasi SeKuNe.

## 🔧 Masalah Instalasi

### Python/Node.js Tidak Terdeteksi

**Gejala:**
```bash
'python' is not recognized as an internal or external command
'node' is not recognized as an internal or external command
```

**Solusi:**
1. **Windows:**
   - Pastikan Python/Node.js sudah diinstall
   - Tambahkan ke PATH environment variable
   - Restart Command Prompt/PowerShell

2. **Linux/macOS:**
   ```bash
   # Cek instalasi
   which python3
   which node
   
   # Install jika belum ada
   sudo apt install python3 nodejs npm  # Ubuntu
   brew install python3 node            # macOS
   ```

### Virtual Environment Error

**Gejala:**
```bash
Error: Unable to create virtual environment
```

**Solusi:**
```bash
# Install venv module
sudo apt install python3-venv  # Ubuntu
pip install virtualenv         # Alternative

# Buat ulang virtual environment
rm -rf venv
python3 -m venv venv
```

### Dependencies Installation Failed

**Gejala:**
```bash
ERROR: Could not install packages due to an EnvironmentError
```

**Solusi:**
```bash
# Update pip
pip install --upgrade pip

# Install dengan user flag
pip install --user -r requirements.txt

# Clear cache dan install ulang
pip cache purge
pip install -r requirements.txt
```

## 🌐 Masalah Koneksi

### Backend Tidak Bisa Diakses

**Gejala:**
- Frontend tidak bisa connect ke backend
- Error "Network Error" atau "Connection Refused"

**Diagnosis:**
```bash
# Cek apakah backend berjalan
curl http://localhost:5000/api/health

# Cek port yang digunakan
netstat -tlnp | grep :5000
lsof -i :5000
```

**Solusi:**
1. **Pastikan backend berjalan:**
   ```bash
   cd sekune_backend
   source venv/bin/activate
   python src/main.py
   ```

2. **Cek konfigurasi CORS:**
   - Pastikan frontend URL ada di CORS_ORIGINS
   - Update file `.env` jika diperlukan

3. **Firewall/Antivirus:**
   - Disable sementara untuk testing
   - Tambahkan exception untuk port 5000 dan 5173

### Frontend Tidak Bisa Diakses

**Gejala:**
- Browser tidak bisa membuka http://localhost:5173
- "This site can't be reached"

**Solusi:**
```bash
# Cek apakah frontend berjalan
curl http://localhost:5173

# Restart development server
cd sekune_frontend
npm run dev
# atau
pnpm run dev
```

### CORS Error

**Gejala:**
```
Access to XMLHttpRequest at 'http://localhost:5000/api/...' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solusi:**
1. **Update backend CORS configuration:**
   ```python
   # Di src/main.py
   CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
   ```

2. **Restart backend setelah perubahan**

## 🔐 Masalah Autentikasi

### Login Gagal

**Gejala:**
- "Invalid credentials" meskipun password benar
- Token tidak valid

**Diagnosis:**
```bash
# Cek database user
sqlite3 sekune.db
.tables
SELECT * FROM users WHERE email = 'admin@sekune.com';
```

**Solusi:**
1. **Reset password admin:**
   ```python
   # Jalankan script Python
   from werkzeug.security import generate_password_hash
   import sqlite3
   
   conn = sqlite3.connect('sekune.db')
   hashed = generate_password_hash('admin123')
   conn.execute("UPDATE users SET password_hash = ? WHERE email = ?", 
                (hashed, 'admin@sekune.com'))
   conn.commit()
   conn.close()
   ```

2. **Cek JWT configuration:**
   - Pastikan JWT_SECRET_KEY diset
   - Cek expiration time

### Session Expired

**Gejala:**
- Otomatis logout setelah beberapa waktu
- "Token expired" error

**Solusi:**
1. **Update JWT expiration:**
   ```python
   # Di .env file
   JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 jam
   ```

2. **Clear browser storage:**
   ```javascript
   // Di browser console
   localStorage.clear()
   sessionStorage.clear()
   ```

## 💾 Masalah Database

### Database File Not Found

**Gejala:**
```bash
sqlite3.OperationalError: no such table: users
```

**Solusi:**
```bash
# Hapus database lama dan buat ulang
rm sekune.db
python src/main.py  # Akan membuat database baru
```

### Database Locked

**Gejala:**
```bash
sqlite3.OperationalError: database is locked
```

**Solusi:**
```bash
# Kill proses yang menggunakan database
lsof sekune.db
kill -9 <PID>

# Atau restart aplikasi
```

### Migration Error

**Gejala:**
- Error saat update schema database
- "Column doesn't exist" error

**Solusi:**
1. **Backup data:**
   ```bash
   cp sekune.db sekune.db.backup
   ```

2. **Reset database:**
   ```bash
   rm sekune.db
   python src/main.py
   ```

3. **Restore data manual jika diperlukan**

## 📁 Masalah File Upload

### File Upload Gagal

**Gejala:**
- "File too large" error
- Upload stuck di 0%

**Solusi:**
1. **Cek ukuran file:**
   - Maksimal 10MB per file
   - Compress file jika terlalu besar

2. **Cek format file:**
   - Pastikan format didukung (PDF, DOC, JPG, PNG)
   - Rename file jika ada karakter khusus

3. **Cek permission direktori:**
   ```bash
   chmod 755 sekune_backend/src/static/uploads/
   chown -R $USER:$USER sekune_backend/src/static/
   ```

### File Tidak Bisa Didownload

**Gejala:**
- Link download tidak berfungsi
- File not found error

**Solusi:**
```bash
# Cek apakah file ada
ls -la sekune_backend/src/static/uploads/

# Cek permission
chmod 644 sekune_backend/src/static/uploads/*
```

## 🎨 Masalah Frontend

### Styling Tidak Muncul

**Gejala:**
- Tampilan berantakan
- CSS tidak load

**Solusi:**
```bash
# Clear cache dan rebuild
cd sekune_frontend
rm -rf node_modules
rm package-lock.json
npm install
npm run dev
```

### JavaScript Error

**Gejala:**
- Console error di browser
- Fitur tidak berfungsi

**Diagnosis:**
1. **Buka Developer Tools (F12)**
2. **Cek Console tab untuk error**
3. **Cek Network tab untuk failed requests**

**Solusi:**
```bash
# Update dependencies
npm update

# Clear cache
npm cache clean --force

# Restart development server
npm run dev
```

### Build Production Gagal

**Gejala:**
```bash
Error: Build failed with errors
```

**Solusi:**
```bash
# Cek error detail
npm run build 2>&1 | tee build.log

# Fix import/export errors
# Update deprecated packages
npm audit fix

# Clean build
rm -rf dist
npm run build
```

## 🔄 Masalah Performance

### Aplikasi Lambat

**Gejala:**
- Loading lama
- Response time tinggi

**Diagnosis:**
```bash
# Cek resource usage
top
htop
free -h
df -h
```

**Solusi:**
1. **Restart aplikasi:**
   ```bash
   # Kill semua proses
   pkill -f "python src/main.py"
   pkill -f "npm run dev"
   
   # Start ulang
   cd sekune_backend && python src/main.py &
   cd sekune_frontend && npm run dev &
   ```

2. **Optimize database:**
   ```bash
   sqlite3 sekune.db "VACUUM;"
   sqlite3 sekune.db "ANALYZE;"
   ```

3. **Clear browser cache:**
   - Ctrl+Shift+Delete (Chrome/Firefox)
   - Clear all browsing data

### Memory Usage Tinggi

**Gejala:**
- System menjadi lambat
- Out of memory error

**Solusi:**
```bash
# Cek memory usage
ps aux --sort=-%mem | head

# Kill proses yang tidak perlu
kill -9 <PID>

# Restart dengan limit memory (jika perlu)
ulimit -v 1000000  # Limit virtual memory
```

## 🌐 Masalah Deployment

### Production Build Error

**Gejala:**
- Build gagal untuk production
- Missing dependencies

**Solusi:**
```bash
# Install production dependencies
cd sekune_backend
pip install gunicorn
pip install -r requirements.txt

cd sekune_frontend
npm ci --production
npm run build
```

### Nginx Configuration Error

**Gejala:**
- 502 Bad Gateway
- Nginx tidak bisa start

**Solusi:**
```bash
# Test nginx config
sudo nginx -t

# Cek error log
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

### SSL Certificate Error

**Gejala:**
- HTTPS tidak berfungsi
- Certificate expired

**Solusi:**
```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Test certificate
sudo certbot certificates

# Restart nginx
sudo systemctl reload nginx
```

## 🔍 Debugging Tools

### Backend Debugging

**Enable Debug Mode:**
```python
# Di src/main.py
app.debug = True
app.run(debug=True)
```

**Check Logs:**
```bash
# Jalankan dengan verbose logging
python src/main.py 2>&1 | tee app.log
```

### Frontend Debugging

**Browser Developer Tools:**
1. **Console**: Lihat JavaScript errors
2. **Network**: Monitor API calls
3. **Application**: Cek localStorage/sessionStorage
4. **Sources**: Debug JavaScript code

**React Developer Tools:**
- Install extension untuk Chrome/Firefox
- Monitor component state dan props

### Database Debugging

**SQLite Commands:**
```bash
sqlite3 sekune.db
.tables                    # List all tables
.schema users             # Show table structure
SELECT * FROM users;      # Query data
.quit                     # Exit
```

## 📞 Mendapatkan Bantuan

### Log Files Location
```
sekune_backend/app.log          # Application logs
/var/log/nginx/error.log        # Nginx errors (production)
~/.npm/_logs/                   # NPM logs
```

### Informasi System
```bash
# Kumpulkan info system untuk bug report
echo "OS: $(uname -a)"
echo "Python: $(python3 --version)"
echo "Node: $(node --version)"
echo "NPM: $(npm --version)"
echo "Disk: $(df -h)"
echo "Memory: $(free -h)"
```

### Membuat Bug Report

**Include informasi berikut:**
1. **Langkah reproduksi error**
2. **Error message lengkap**
3. **Screenshot jika perlu**
4. **System information**
5. **Log files yang relevan**

### Kontak Support
- **GitHub Issues**: Untuk bug report dan feature request
- **Email**: support@sekolah.edu (jika tersedia)
- **Documentation**: Cek manual user untuk solusi umum

---

**Tips:** Selalu backup data sebelum melakukan troubleshooting yang melibatkan perubahan database atau file system!

