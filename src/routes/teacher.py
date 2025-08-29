from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.models import (
    Assignment, Submission, Quiz, QuizQuestion, QuizAttempt, Grade, Message, 
    Student, Teacher, Subject, GradeType, QuestionType, db
)
from src.utils.auth import teacher_required, get_current_user
from datetime import datetime

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/assignments', methods=['POST'])
@teacher_required
def create_assignment():
    """Membuat tugas baru"""
    try:
        current_user = get_current_user()
        teacher = current_user.teacher
        
        if not teacher:
            return jsonify({'message': 'Data guru tidak ditemukan'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Data tidak boleh kosong'}), 400
        
        required_fields = ['title', 'description', 'due_date', 'rombel_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Field {field} harus diisi'}), 400
        
        # Parse due_date
        try:
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Format due_date tidak valid'}), 400
        
        assignment = Assignment(
            title=data['title'],
            description=data['description'],
            due_date=due_date,
            teacher_id=teacher.id,
            rombel_id=data['rombel_id'],
            file_attachment_url=data.get('file_attachment_url')
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify({
            'message': 'Tugas berhasil dibuat',
            'assignment': assignment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@teacher_bp.route('/assignments', methods=['GET'])
@teacher_required
def get_assignments():
    """Melihat daftar tugas yang dibuat guru"""
    try:
        current_user = get_current_user()
        teacher = current_user.teacher
        
        if not teacher:
            return jsonify({'message': 'Data guru tidak ditemukan'}), 404
        
        assignments = Assignment.query.filter_by(teacher_id=teacher.id).all()
        
        return jsonify({'assignments': [assignment.to_dict() for assignment in assignments]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@teacher_bp.route('/assignments/<assignment_id>', methods=['PUT'])
@teacher_required
def update_assignment(assignment_id):
    """Update tugas"""
    try:
        current_user = get_current_user()
        teacher = current_user.teacher
        
        if not teacher:
            return jsonify({'message': 'Data guru tidak ditemukan'}), 404
        
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'message': 'Tugas tidak ditemukan'}), 404
        
        # Pastikan tugas milik guru ini
        if assignment.teacher_id != teacher.id:
            return jsonify({'message': 'Akses ditolak'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Data tidak boleh kosong'}), 400
        
        if 'title' in data:
            assignment.title = data['title']
        if 'description' in data:
            assignment.description = data['description']
        if 'due_date' in data:
            try:
                assignment.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'message': 'Format due_date tidak valid'}), 400
        if 'file_attachment_url' in data:
            assignment.file_attachment_url = data['file_attachment_url']
        
        assignment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Tugas berhasil diupdate',
            'assignment': assignment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@teacher_bp.route('/assignments/<assignment_id>/submissions', methods=['GET'])
@teacher_required
def get_assignment_submissions(assignment_id):
    """Melihat pengumpulan tugas"""
    try:
        current_user = get_current_user()
        teacher = current_user.teacher
        
        if not teacher:
            return jsonify({'message': 'Data guru tidak ditemukan'}), 404
        
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'message': 'Tugas tidak ditemukan'}), 404
        
        # Pastikan tugas milik guru ini
        if assignment.teacher_id != teacher.id:
            return jsonify({'message': 'Akses ditolak'}), 403
        
        submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
        
        return jsonify({
            'assignment': assignment.to_dict(),
            'submissions': [submission.to_dict() for submission in submissions]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@teacher_bp.route('/submissions/<submission_id>/grade', methods=['PUT'])
@teacher_required
def grade_submission(submission_id):
    """Memberi nilai tugas"""
    try:
        current_user = get_current_user()
        teacher = current_user.teacher
        
        if not teacher:
            return jsonify({'message': 'Data guru tidak ditemukan'}), 404
        
        submission = Submission.query.get(submission_id)
        if not submission:
            return jsonify({'message': 'Submission tidak ditemukan'}), 404
        
        # Pastikan tugas milik guru ini
        if submission.assignment.teacher_id != teacher.id:
            return jsonify({'message': 'Akses ditolak'}), 403
        
        data = request.get_json()
        if not data or 'grade' not in data:
            return jsonify({'message': 'Nilai harus diisi'}), 400
        
        try:
            grade_value = float(data['grade'])
            if grade_value < 0 or grade_value > 100:
                return jsonify({'message': 'Nilai harus antara 0-100'}), 400
        except ValueError:
            return jsonify({'message': 'Format nilai tidak valid'}), 400
        
        # Update submission
        submission.grade = grade_value
        submission.feedback = data.get('feedback')
        submission.updated_at = datetime.utcnow()
        
        # Buat record grade
        grade = Grade(
            student_id=submission.student_id,
            teacher_id=teacher.id,
            type=GradeType.ASSIGNMENT,
            source_id=submission.id,
            value=grade_value,
            description=f'Nilai tugas: {submission.assignment.title}',
            graded_at=datetime.utcnow()
        )
        
        db.session.add(grade)
        db.session.commit()
        
        return jsonify({
            'message': 'Nilai berhasil diberikan',
            'submission': submission.to_dict(),
            'grade': grade.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@teacher_bp.route('/quizzes', methods=['POST'])
@teacher_required
def create_quiz():
    """Membuat kuis baru"""
    try:
        current_user = get_current_user()
        teacher = current_user.teacher
        
        if not teacher:
            return jsonify({'message': 'Data guru tidak ditemukan'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Data tidak boleh kosong'}), 400
        
        required_fields = ['title', 'rombel_id', 'duration_per_question', 'questions']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Field {field} harus diisi'}), 400
        
        if not isinstance(data['questions'], list) or len(data['questions']) == 0:
            return jsonify({'message': 'Minimal harus ada 1 soal'}), 400
        
        # Buat kuis
        quiz = Quiz(
            title=data['title'],
            description=data.get('description'),
            teacher_id=teacher.id,
            rombel_id=data['rombel_id'],
            duration_per_question=data['duration_per_question'],
            start_time=datetime.fromisoformat(data['start_time'].replace('Z', '+00:00')) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time'].replace('Z', '+00:00')) if data.get('end_time') else None
        )
        
        db.session.add(quiz)
        db.session.flush()  # Untuk mendapatkan ID
        
        # Buat soal-soal
        for i, question_data in enumerate(data['questions']):
            if not question_data.get('question_text') or not question_data.get('correct_answer'):
                return jsonify({'message': f'Soal ke-{i+1} tidak lengkap'}), 400
            
            question_type = QuestionType.MULTIPLE_CHOICE
            if question_data.get('question_type') == 'true_false':
                question_type = QuestionType.TRUE_FALSE
            elif question_data.get('question_type') == 'short_answer':
                question_type = QuestionType.SHORT_ANSWER
            
            question = QuizQuestion(
                quiz_id=quiz.id,
                question_text=question_data['question_text'],
                question_type=question_type,
                options=question_data.get('options'),
                correct_answer=question_data['correct_answer'],
                order=i + 1
            )
            
            db.session.add(question)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Kuis berhasil dibuat',
            'quiz': quiz.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@teacher_bp.route('/quizzes', methods=['GET'])
@teacher_required
def get_quizzes():
    """Melihat daftar kuis yang dibuat guru"""
    try:
        current_user = get_current_user()
        teacher = current_user.teacher
        
        if not teacher:
            return jsonify({'message': 'Data guru tidak ditemukan'}), 404
        
        quizzes = Quiz.query.filter_by(teacher_id=teacher.id).all()
        
        return jsonify({'quizzes': [quiz.to_dict() for quiz in quizzes]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@teacher_bp.route('/grades/offline', methods=['POST'])
@teacher_required
def input_offline_grade():
    """Input nilai offline"""
    try:
        current_user = get_current_user()
        teacher = current_user.teacher
        
        if not teacher:
            return jsonify({'message': 'Data guru tidak ditemukan'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Data tidak boleh kosong'}), 400
        
        required_fields = ['student_id', 'value', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Field {field} harus diisi'}), 400
        
        # Validasi student
        student = Student.query.get(data['student_id'])
        if not student:
            return jsonify({'message': 'Siswa tidak ditemukan'}), 404
        
        try:
            grade_value = float(data['value'])
            if grade_value < 0 or grade_value > 100:
                return jsonify({'message': 'Nilai harus antara 0-100'}), 400
        except ValueError:
            return jsonify({'message': 'Format nilai tidak valid'}), 400
        
        grade = Grade(
            student_id=data['student_id'],
            subject_id=data.get('subject_id'),
            teacher_id=teacher.id,
            type=GradeType.OFFLINE,
            value=grade_value,
            description=data['description'],
            graded_at=datetime.utcnow()
        )
        
        db.session.add(grade)
        db.session.commit()
        
        return jsonify({
            'message': 'Nilai offline berhasil diinput',
            'grade': grade.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@teacher_bp.route('/messages', methods=['GET'])
@teacher_required
def get_messages():
    """Melihat pesan guru"""
    try:
        current_user = get_current_user()
        
        # Ambil pesan yang diterima guru
        messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.sent_at.desc()).all()
        
        return jsonify({'messages': [message.to_dict() for message in messages]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@teacher_bp.route('/messages', methods=['POST'])
@teacher_required
def send_message():
    """Mengirim pesan"""
    try:
        current_user = get_current_user()
        
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'message': 'Konten pesan harus diisi'}), 400
        
        message = Message(
            sender_id=current_user.id,
            receiver_id=data.get('receiver_id'),
            rombel_id=data.get('rombel_id'),
            content=data['content'],
            sent_at=datetime.utcnow()
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': 'Pesan berhasil dikirim',
            'data': message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@teacher_bp.route('/announcements', methods=['POST'])
@teacher_required
def send_announcement():
    """Mengirim pengumuman ke seluruh siswa di kelas"""
    try:
        current_user = get_current_user()
        teacher = current_user.teacher
        
        if not teacher:
            return jsonify({'message': 'Data guru tidak ditemukan'}), 404
        
        data = request.get_json()
        if not data or not data.get('content') or not data.get('rombel_id'):
            return jsonify({'message': 'Konten dan rombel_id harus diisi'}), 400
        
        message = Message(
            sender_id=current_user.id,
            rombel_id=data['rombel_id'],
            content=data['content'],
            sent_at=datetime.utcnow()
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': 'Pengumuman berhasil dikirim',
            'data': message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@teacher_bp.route('/dashboard/rombel-performance', methods=['GET'])
@teacher_required
def get_rombel_performance():
    """Dashboard Wali Kelas - ringkasan performa akademik siswa"""
    try:
        current_user = get_current_user()
        teacher = current_user.teacher
        
        if not teacher or not teacher.is_wali_kelas:
            return jsonify({'message': 'Akses hanya untuk Wali Kelas'}), 403
        
        # Ambil rombel yang diampu sebagai wali kelas
        from src.models.models import Rombel
        rombel = Rombel.query.filter_by(wali_kelas_id=teacher.id).first()
        
        if not rombel:
            return jsonify({'message': 'Tidak ada rombel yang diampu'}), 404
        
        # Ambil semua siswa di rombel
        students = Student.query.filter_by(rombel_id=rombel.id).all()
        
        students_performance = []
        for student in students:
            # Hitung rata-rata nilai per siswa
            grades = Grade.query.filter_by(student_id=student.id).all()
            
            if grades:
                total_grade = sum(float(grade.value) for grade in grades)
                average_grade = total_grade / len(grades)
            else:
                average_grade = 0
            
            students_performance.append({
                'student': student.to_dict(),
                'average_grade': round(average_grade, 2),
                'total_grades': len(grades)
            })
        
        return jsonify({
            'rombel': rombel.to_dict(),
            'students_performance': students_performance
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

