# SeKuNe - Sekolah Ku Online

Platform digital untuk memfasilitasi kegiatan belajar mengajar, komunikasi, dan administrasi sekolah dengan empat peran pengguna utama: Siswa, Guru, Orang Tua, dan Administrator.

## 🚀 Fitur Utama

### Portal Administrator
- **Manajemen Pengguna Terpusat**: Pendaftaran dan pengelolaan siswa, guru, orang tua
- **Manajemen Rombel**: Pengelolaan kelas dan wali kelas
- **Pengaturan Sistem**: Kustomisasi identitas sekolah (nama & logo)
- **Manajemen Mata Pelajaran**: Pengelolaan daftar mata pelajaran

### Portal Guru
- **Manajemen Tugas**: Membuat tugas terstruktur dengan tenggat waktu fleksibel
- **Kuis Interaktif**: Membuat kuis dengan batas waktu per soal dan ranking live
- **Input Nilai Offline**: Memasukkan nilai dari aktivitas di luar platform
- **Komunikasi**: Grup kelas, pengumuman, dan pesan pribadi
- **Dashboard Wali Kelas**: Ringkasan performa akademik siswa

### Portal Siswa
- **Tugas Online**: Menerima dan mengumpulkan tugas (file atau teks langsung)
- **Kuis Interaktif**: Mengerjakan kuis dengan sistem penilaian otomatis
- **Komunikasi**: Grup kelas otomatis dan pesan pribadi
- **Monitoring Nilai**: Melihat nilai dan perkembangan akademik

### Portal Orang Tua
- **Monitoring Nilai Anak**: Rekapitulasi nilai (ringkas & terperinci)
- **Visualisasi Grafis**: Tampilan grafis perkembangan akademik anak
- **Komunikasi**: Komunikasi dengan Wali Kelas (pribadi & grup)

## 🛠 Teknologi Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT (JSON Web Tokens)
- **API**: RESTful API
- **Real-time**: Flask-SocketIO (untuk fitur chat dan kuis live)

### Frontend
- **Framework**: React.js
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: React Context + React Query
- **Routing**: React Router DOM
- **HTTP Client**: Axios

### Database Schema
- **Users**: Sistem autentikasi multi-role
- **Students, Teachers, Parents, Admins**: Profil pengguna berdasarkan role
- **Rombels**: Manajemen kelas/rombongan belajar
- **Assignments & Submissions**: Sistem tugas dan pengumpulan
- **Quizzes & Quiz Attempts**: Sistem kuis interaktif
- **Grades**: Sistem penilaian terintegrasi
- **Messages**: Sistem komunikasi real-time

## 📋 Persyaratan Sistem

### Minimum Requirements
- **OS**: Ubuntu 18.04+ / Windows 10+ / macOS 10.14+
- **Python**: 3.8+
- **Node.js**: 16+
- **RAM**: 2GB
- **Storage**: 1GB free space

### Recommended Requirements
- **OS**: Ubuntu 20.04+ / Windows 11 / macOS 12+
- **Python**: 3.11+
- **Node.js**: 18+
- **RAM**: 4GB+
- **Storage**: 5GB+ free space

## 🔐 Akun Demo

Setelah instalasi, gunakan akun berikut untuk testing:

**Administrator**
- Email: `admin@sekune.com`
- Password: `admin123`

## 📚 Dokumentasi

1. [Panduan Instalasi Server](docs/INSTALLATION.md)
2. [Manual Penggunaan Administrator](docs/ADMIN_MANUAL.md)
3. [Manual Penggunaan Guru](docs/TEACHER_MANUAL.md)
4. [Docker Deployment Guide](docs/DOCKER.md)
5. [API Documentation](docs/API.md)
6. [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
git clone https://github.com/Chievo4051/SuKuNe.git
cd SuKuNe
make install
```

Akses aplikasi di http://localhost

### Option 2: Manual Installation

#### 1. Clone Repository
```bash
git clone https://github.com/Chievo4051/SuKuNe.git
cd SuKuNe
```

#### 2. Setup Backend
```bash
cd sekune_backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python src/main.py
```

#### 3. Setup Frontend
```bash
cd sekune_frontend
npm install
npm run dev
```

#### 4. Akses Aplikasi
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## 🏗 Struktur Proyek

```
sekune/
├── sekune_backend/          # Backend Flask API
│   ├── src/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── utils/          # Utilities (auth, helpers)
│   │   ├── static/         # Frontend build files
│   │   └── main.py         # Entry point
│   ├── requirements.txt
│   └── README.md
├── sekune_frontend/         # Frontend React App
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── lib/            # Utilities (API, auth)
│   │   └── App.jsx         # Main app component
│   ├── package.json
│   └── README.md
└── docs/                   # Documentation
    ├── INSTALLATION.md
    ├── ADMIN_MANUAL.md
    ├── TEACHER_MANUAL.md
    └── API.md
```

## 🤝 Kontribusi

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📄 Lisensi

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Kontak & Support

Untuk pertanyaan, bug report, atau feature request, silakan buat issue di repository ini.

---

**SeKuNe** - Memudahkan pengelolaan sekolah digital untuk masa depan pendidikan yang lebih baik.

