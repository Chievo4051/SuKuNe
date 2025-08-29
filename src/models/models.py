from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    SISWA = 'siswa'
    GURU = 'guru'
    ORANG_TUA = 'orang_tua'
    ADMIN = 'admin'

class GradeType(Enum):
    ASSIGNMENT = 'assignment'
    QUIZ = 'quiz'
    OFFLINE = 'offline'
    OTHER = 'other'

class QuestionType(Enum):
    MULTIPLE_CHOICE = 'multiple_choice'
    TRUE_FALSE = 'true_false'
    SHORT_ANSWER = 'short_answer'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='user', uselist=False)
    teacher = db.relationship('Teacher', backref='user', uselist=False)
    parent = db.relationship('Parent', backref='user', uselist=False)
    admin = db.relationship('Admin', backref='user', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(50), nullable=True)
    parent_id = db.Column(db.String(36), db.ForeignKey('parents.id'), nullable=True)
    rombel_id = db.Column(db.String(36), db.ForeignKey('rombels.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'nickname': self.nickname,
            'parent_id': self.parent_id,
            'rombel_id': self.rombel_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_wali_kelas = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'is_wali_kelas': self.is_wali_kelas,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Parent(db.Model):
    __tablename__ = 'parents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    children = db.relationship('Student', backref='parent')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Rombel(db.Model):
    __tablename__ = 'rombels'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)
    wali_kelas_id = db.Column(db.String(36), db.ForeignKey('teachers.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='rombel')
    wali_kelas = db.relationship('Teacher', backref='rombel_wali_kelas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'wali_kelas_id': self.wali_kelas_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Many-to-Many relationship tables
teacher_subjects = db.Table('teacher_subjects',
    db.Column('teacher_id', db.String(36), db.ForeignKey('teachers.id'), primary_key=True),
    db.Column('subject_id', db.String(36), db.ForeignKey('subjects.id'), primary_key=True)
)

rombel_teachers = db.Table('rombel_teachers',
    db.Column('rombel_id', db.String(36), db.ForeignKey('rombels.id'), primary_key=True),
    db.Column('teacher_id', db.String(36), db.ForeignKey('teachers.id'), primary_key=True)
)

rombel_subjects = db.Table('rombel_subjects',
    db.Column('rombel_id', db.String(36), db.ForeignKey('rombels.id'), primary_key=True),
    db.Column('subject_id', db.String(36), db.ForeignKey('subjects.id'), primary_key=True)
)

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    teacher_id = db.Column(db.String(36), db.ForeignKey('teachers.id'), nullable=False)
    rombel_id = db.Column(db.String(36), db.ForeignKey('rombels.id'), nullable=False)
    file_attachment_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('Teacher', backref='assignments')
    rombel = db.relationship('Rombel', backref='assignments')
    submissions = db.relationship('Submission', backref='assignment')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat(),
            'teacher_id': self.teacher_id,
            'rombel_id': self.rombel_id,
            'file_attachment_url': self.file_attachment_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = db.Column(db.String(36), db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False)
    submission_content = db.Column(db.Text, nullable=True)
    file_submission_url = db.Column(db.String(500), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Numeric(5, 2), nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='submissions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'submission_content': self.submission_content,
            'file_submission_url': self.file_submission_url,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'grade': float(self.grade) if self.grade else None,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.String(36), db.ForeignKey('teachers.id'), nullable=False)
    rombel_id = db.Column(db.String(36), db.ForeignKey('rombels.id'), nullable=False)
    duration_per_question = db.Column(db.Integer, nullable=False)  # dalam detik
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('Teacher', backref='quizzes')
    rombel = db.relationship('Rombel', backref='quizzes')
    questions = db.relationship('QuizQuestion', backref='quiz')
    attempts = db.relationship('QuizAttempt', backref='quiz')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'rombel_id': self.rombel_id,
            'duration_per_question': self.duration_per_question,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum(QuestionType), nullable=False)
    options = db.Column(db.JSON, nullable=True)  # Untuk multiple choice
    correct_answer = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_text': self.question_text,
            'question_type': self.question_type.value,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'order': self.order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'), nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False)
    score = db.Column(db.Numeric(5, 2), nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='quiz_attempts')
    answers = db.relationship('QuizAnswer', backref='attempt')
    
    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'student_id': self.student_id,
            'score': float(self.score) if self.score else None,
            'started_at': self.started_at.isoformat(),
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    attempt_id = db.Column(db.String(36), db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.String(36), db.ForeignKey('quiz_questions.id'), nullable=False)
    student_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=True)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('QuizQuestion', backref='answers')
    
    def to_dict(self):
        return {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'question_id': self.question_id,
            'student_answer': self.student_answer,
            'is_correct': self.is_correct,
            'answered_at': self.answered_at.isoformat()
        }

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.String(36), db.ForeignKey('subjects.id'), nullable=True)
    teacher_id = db.Column(db.String(36), db.ForeignKey('teachers.id'), nullable=True)
    type = db.Column(db.Enum(GradeType), nullable=False)
    source_id = db.Column(db.String(36), nullable=True)  # FK ke submissions.id atau quiz_attempts.id
    value = db.Column(db.Numeric(5, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    graded_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='grades')
    subject = db.relationship('Subject', backref='grades')
    teacher = db.relationship('Teacher', backref='grades_given')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'teacher_id': self.teacher_id,
            'type': self.type.value,
            'source_id': self.source_id,
            'value': float(self.value),
            'description': self.description,
            'graded_at': self.graded_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)  # Untuk pesan pribadi
    rombel_id = db.Column(db.String(36), db.ForeignKey('rombels.id'), nullable=True)  # Untuk pesan grup kelas
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    rombel = db.relationship('Rombel', backref='messages')
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'rombel_id': self.rombel_id,
            'content': self.content,
            'sent_at': self.sent_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SchoolSettings(db.Model):
    __tablename__ = 'school_settings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_name = db.Column(db.String(200), nullable=False)
    school_logo_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_name': self.school_name,
            'school_logo_url': self.school_logo_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

