# API Documentation SeKuNe

Dokumentasi lengkap REST API untuk aplikasi SeKuNe. API ini menyediakan endpoint untuk semua fitur aplikasi dengan autentikasi JWT.

## 🔐 Authentication

### Base URL
```
http://localhost:5000/api
```

### Authentication Header
Semua endpoint yang memerlukan autentikasi harus menyertakan header:
```
Authorization: Bearer <jwt_token>
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "admin"
  },
  "profile": {
    "id": 1,
    "name": "Administrator"
  }
}
```

### Get Profile
```http
GET /auth/me
Authorization: Bearer <token>
```

### Logout
```http
POST /auth/logout
Authorization: Bearer <token>
```

## 👥 Admin Endpoints

### Users Management

#### Get All Users
```http
GET /admin/users
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "email": "teacher@school.com",
      "role": "guru",
      "profile": {
        "id": 1,
        "name": "Guru Matematika"
      }
    }
  ]
}
```

#### Create User
```http
POST /admin/users
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "type": "guru",
  "nama_guru": "John Doe",
  "email_guru": "john@school.com",
  "password": "password123"
}
```

**For Student & Parent:**
```json
{
  "type": "siswa_orang_tua",
  "nama_siswa": "Jane Doe",
  "nickname": "Jane",
  "email_siswa": "jane@school.com",
  "password_siswa": "password123",
  "nama_orang_tua": "Mr. Doe",
  "email_orang_tua": "mrdoe@email.com",
  "password_orang_tua": "password123",
  "rombel_id": "1"
}
```

#### Update User
```http
PUT /admin/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "email": "updated@email.com"
}
```

### Rombel Management

#### Get All Rombels
```http
GET /admin/rombels
Authorization: Bearer <admin_token>
```

#### Create Rombel
```http
POST /admin/rombels
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "7 A",
  "wali_kelas_id": "1"
}
```

#### Update Rombel
```http
PUT /admin/rombels/{rombel_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "7 A Updated",
  "wali_kelas_id": "2"
}
```

#### Delete Rombel
```http
DELETE /admin/rombels/{rombel_id}
Authorization: Bearer <admin_token>
```

### Subject Management

#### Get All Subjects
```http
GET /admin/subjects
Authorization: Bearer <admin_token>
```

#### Create Subject
```http
POST /admin/subjects
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Matematika"
}
```

### School Settings

#### Get School Settings
```http
GET /admin/school-settings
Authorization: Bearer <admin_token>
```

#### Update School Settings
```http
PUT /admin/school-settings
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "school_name": "SMA Negeri 1",
  "school_logo_url": "https://example.com/logo.png"
}
```

## 👨‍🏫 Teacher Endpoints

### Assignment Management

#### Get Teacher's Assignments
```http
GET /teacher/assignments
Authorization: Bearer <teacher_token>
```

#### Create Assignment
```http
POST /teacher/assignments
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "title": "Tugas Matematika Bab 1",
  "description": "Kerjakan soal halaman 15-20",
  "subject_id": 1,
  "rombel_id": 1,
  "due_date": "2024-01-15T23:59:59",
  "max_score": 100,
  "submission_type": "file"
}
```

#### Update Assignment
```http
PUT /teacher/assignments/{assignment_id}
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description",
  "due_date": "2024-01-20T23:59:59"
}
```

#### Get Assignment Submissions
```http
GET /teacher/assignments/{assignment_id}/submissions
Authorization: Bearer <teacher_token>
```

#### Grade Submission
```http
PUT /teacher/submissions/{submission_id}/grade
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "score": 85,
  "feedback": "Good work! Need improvement on question 3."
}
```

### Quiz Management

#### Get Teacher's Quizzes
```http
GET /teacher/quizzes
Authorization: Bearer <teacher_token>
```

#### Create Quiz
```http
POST /teacher/quizzes
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "title": "Kuis Matematika Bab 1",
  "description": "Kuis tentang aljabar dasar",
  "subject_id": 1,
  "rombel_id": 1,
  "start_time": "2024-01-10T08:00:00",
  "end_time": "2024-01-10T09:00:00",
  "duration_minutes": 60,
  "questions": [
    {
      "question": "Berapa hasil dari 2 + 2?",
      "type": "multiple_choice",
      "options": ["3", "4", "5", "6"],
      "correct_answer": "4",
      "points": 10
    }
  ]
}
```

### Grade Management

#### Input Offline Grade
```http
POST /teacher/grades/offline
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "student_id": 1,
  "subject_id": 1,
  "grade_type": "ulangan_harian",
  "score": 85,
  "max_score": 100,
  "date": "2024-01-10",
  "description": "Ulangan Harian Bab 1"
}
```

### Communication

#### Get Messages
```http
GET /teacher/messages
Authorization: Bearer <teacher_token>
```

#### Send Message
```http
POST /teacher/messages
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "recipient_id": 1,
  "recipient_type": "student",
  "message": "Jangan lupa kerjakan tugas matematika ya!"
}
```

#### Send Announcement
```http
POST /teacher/announcements
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "rombel_id": 1,
  "title": "Pengumuman Penting",
  "message": "Besok ada ulangan matematika, jangan lupa belajar!"
}
```

### Dashboard

#### Get Rombel Performance
```http
GET /teacher/dashboard/rombel-performance
Authorization: Bearer <teacher_token>
```

## 👨‍🎓 Student Endpoints

### Assignment

#### Get Student's Assignments
```http
GET /student/assignments
Authorization: Bearer <student_token>
```

#### Get Assignment Detail
```http
GET /student/assignments/{assignment_id}
Authorization: Bearer <student_token>
```

#### Submit Assignment
```http
POST /student/assignments/{assignment_id}/submit
Authorization: Bearer <student_token>
Content-Type: multipart/form-data

{
  "submission_text": "Jawaban tugas...",
  "file": <file_upload>
}
```

### Quiz

#### Get Student's Quizzes
```http
GET /student/quizzes
Authorization: Bearer <student_token>
```

#### Start Quiz
```http
POST /student/quizzes/{quiz_id}/start
Authorization: Bearer <student_token>
```

#### Submit Quiz Answer
```http
POST /student/quizzes/{quiz_id}/submit-answer
Authorization: Bearer <student_token>
Content-Type: application/json

{
  "question_id": 1,
  "answer": "4"
}
```

#### Finish Quiz
```http
POST /student/quizzes/{quiz_id}/finish
Authorization: Bearer <student_token>
```

### Grades

#### Get Student's Grades
```http
GET /student/grades
Authorization: Bearer <student_token>
```

### Communication

#### Get Messages
```http
GET /student/messages
Authorization: Bearer <student_token>
```

#### Send Message
```http
POST /student/messages
Authorization: Bearer <student_token>
Content-Type: application/json

{
  "recipient_id": 1,
  "recipient_type": "teacher",
  "message": "Pak, saya mau tanya tentang tugas kemarin"
}
```

## 👨‍👩‍👧‍👦 Parent Endpoints

### Children Management

#### Get Parent's Children
```http
GET /parent/children
Authorization: Bearer <parent_token>
```

### Grades Monitoring

#### Get Child's Grades
```http
GET /parent/children/{student_id}/grades
Authorization: Bearer <parent_token>
```

#### Get Child's Grades Summary
```http
GET /parent/children/{student_id}/grades/summary
Authorization: Bearer <parent_token>
```

### Communication

#### Get Messages
```http
GET /parent/messages
Authorization: Bearer <parent_token>
```

#### Send Message
```http
POST /parent/messages
Authorization: Bearer <parent_token>
Content-Type: application/json

{
  "recipient_id": 1,
  "recipient_type": "teacher",
  "message": "Selamat pagi Bu, saya ingin konsultasi tentang perkembangan anak saya"
}
```

#### Get Child's Wali Kelas
```http
GET /parent/children/{student_id}/wali-kelas
Authorization: Bearer <parent_token>
```

#### Get Rombel Messages
```http
GET /parent/rombel-messages/{rombel_id}
Authorization: Bearer <parent_token>
```

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    // response data
  },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Email is required"]
    }
  }
}
```

## 🔒 Error Codes

| Code | Description |
|------|-------------|
| `UNAUTHORIZED` | Invalid or missing authentication token |
| `FORBIDDEN` | User doesn't have permission for this action |
| `VALIDATION_ERROR` | Request data validation failed |
| `NOT_FOUND` | Requested resource not found |
| `DUPLICATE_ENTRY` | Trying to create duplicate data |
| `SERVER_ERROR` | Internal server error |

## 📝 Data Models

### User
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "admin|guru|siswa|orang_tua",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Assignment
```json
{
  "id": 1,
  "title": "Tugas Matematika",
  "description": "Kerjakan soal...",
  "subject_id": 1,
  "teacher_id": 1,
  "rombel_id": 1,
  "due_date": "2024-01-15T23:59:59Z",
  "max_score": 100,
  "submission_type": "file|text|both",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Quiz
```json
{
  "id": 1,
  "title": "Kuis Matematika",
  "description": "Kuis tentang...",
  "subject_id": 1,
  "teacher_id": 1,
  "rombel_id": 1,
  "start_time": "2024-01-10T08:00:00Z",
  "end_time": "2024-01-10T09:00:00Z",
  "duration_minutes": 60,
  "questions": [...],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Grade
```json
{
  "id": 1,
  "student_id": 1,
  "subject_id": 1,
  "teacher_id": 1,
  "grade_type": "assignment|quiz|offline",
  "score": 85,
  "max_score": 100,
  "date": "2024-01-10",
  "description": "Tugas Bab 1",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🔧 Rate Limiting

API menggunakan rate limiting untuk mencegah abuse:
- **General endpoints**: 100 requests per minute
- **Authentication**: 10 requests per minute
- **File upload**: 5 requests per minute

## 📱 CORS Configuration

API mendukung CORS untuk akses dari frontend:
```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

## 🧪 Testing

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### API Testing Tools
- **Postman Collection**: Available in `/docs/postman/`
- **Swagger UI**: Available at `/api/docs` (if enabled)
- **cURL Examples**: Available in `/docs/curl-examples.md`

---

**API Documentation SeKuNe v1.0** - Untuk pertanyaan atau bug report, silakan buat issue di repository GitHub.

