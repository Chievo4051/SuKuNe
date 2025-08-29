from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.models import (
    Assignment, Submission, Quiz, QuizAttempt, QuizAnswer, QuizQuestion, 
    Grade, Message, Student, db
)
from src.utils.auth import student_required, get_current_user
from datetime import datetime

student_bp = Blueprint('student', __name__)

@student_bp.route('/assignments', methods=['GET'])
@student_required
def get_assignments():
    """Melihat daftar tugas untuk siswa"""
    try:
        current_user = get_current_user()
        student = current_user.student
        
        if not student:
            return jsonify({'message': 'Data siswa tidak ditemukan'}), 404
        
        # Ambil tugas berdasarkan rombel siswa
        assignments = Assignment.query.filter_by(rombel_id=student.rombel_id).all()
        
        assignments_data = []
        for assignment in assignments:
            assignment_data = assignment.to_dict()
            
            # Cek apakah siswa sudah mengumpulkan tugas
            submission = Submission.query.filter_by(
                assignment_id=assignment.id,
                student_id=student.id
            ).first()
            
            assignment_data['submitted'] = submission is not None
            if submission:
                assignment_data['submission'] = submission.to_dict()
            
            assignments_data.append(assignment_data)
        
        return jsonify({'assignments': assignments_data}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@student_bp.route('/assignments/<assignment_id>', methods=['GET'])
@student_required
def get_assignment_detail(assignment_id):
    """Melihat detail tugas"""
    try:
        current_user = get_current_user()
        student = current_user.student
        
        if not student:
            return jsonify({'message': 'Data siswa tidak ditemukan'}), 404
        
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'message': 'Tugas tidak ditemukan'}), 404
        
        # Pastikan tugas untuk rombel siswa
        if assignment.rombel_id != student.rombel_id:
            return jsonify({'message': 'Akses ditolak'}), 403
        
        assignment_data = assignment.to_dict()
        
        # Cek submission siswa
        submission = Submission.query.filter_by(
            assignment_id=assignment.id,
            student_id=student.id
        ).first()
        
        assignment_data['submitted'] = submission is not None
        if submission:
            assignment_data['submission'] = submission.to_dict()
        
        return jsonify({'assignment': assignment_data}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@student_bp.route('/assignments/<assignment_id>/submit', methods=['POST'])
@student_required
def submit_assignment(assignment_id):
    """Mengumpulkan tugas"""
    try:
        current_user = get_current_user()
        student = current_user.student
        
        if not student:
            return jsonify({'message': 'Data siswa tidak ditemukan'}), 404
        
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'message': 'Tugas tidak ditemukan'}), 404
        
        # Pastikan tugas untuk rombel siswa
        if assignment.rombel_id != student.rombel_id:
            return jsonify({'message': 'Akses ditolak'}), 403
        
        # Cek apakah sudah melewati deadline
        if datetime.utcnow() > assignment.due_date:
            return jsonify({'message': 'Tugas sudah melewati batas waktu'}), 400
        
        # Cek apakah sudah pernah submit
        existing_submission = Submission.query.filter_by(
            assignment_id=assignment.id,
            student_id=student.id
        ).first()
        
        if existing_submission:
            return jsonify({'message': 'Tugas sudah pernah dikumpulkan'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Data tidak boleh kosong'}), 400
        
        # Validasi minimal ada content atau file
        if not data.get('submission_content') and not data.get('file_submission_url'):
            return jsonify({'message': 'Harus ada jawaban atau file yang dikirim'}), 400
        
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student.id,
            submission_content=data.get('submission_content'),
            file_submission_url=data.get('file_submission_url'),
            submitted_at=datetime.utcnow()
        )
        
        db.session.add(submission)
        db.session.commit()
        
        return jsonify({
            'message': 'Tugas berhasil dikumpulkan',
            'submission': submission.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@student_bp.route('/quizzes', methods=['GET'])
@student_required
def get_quizzes():
    """Melihat daftar kuis untuk siswa"""
    try:
        current_user = get_current_user()
        student = current_user.student
        
        if not student:
            return jsonify({'message': 'Data siswa tidak ditemukan'}), 404
        
        # Ambil kuis berdasarkan rombel siswa
        quizzes = Quiz.query.filter_by(rombel_id=student.rombel_id).all()
        
        quizzes_data = []
        for quiz in quizzes:
            quiz_data = quiz.to_dict()
            
            # Cek apakah siswa sudah mengerjakan kuis
            attempt = QuizAttempt.query.filter_by(
                quiz_id=quiz.id,
                student_id=student.id
            ).first()
            
            quiz_data['attempted'] = attempt is not None
            if attempt:
                quiz_data['attempt'] = attempt.to_dict()
            
            quizzes_data.append(quiz_data)
        
        return jsonify({'quizzes': quizzes_data}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@student_bp.route('/quizzes/<quiz_id>/start', methods=['POST'])
@student_required
def start_quiz(quiz_id):
    """Memulai kuis"""
    try:
        current_user = get_current_user()
        student = current_user.student
        
        if not student:
            return jsonify({'message': 'Data siswa tidak ditemukan'}), 404
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'message': 'Kuis tidak ditemukan'}), 404
        
        # Pastikan kuis untuk rombel siswa
        if quiz.rombel_id != student.rombel_id:
            return jsonify({'message': 'Akses ditolak'}), 403
        
        # Cek apakah sudah pernah mengerjakan
        existing_attempt = QuizAttempt.query.filter_by(
            quiz_id=quiz.id,
            student_id=student.id
        ).first()
        
        if existing_attempt:
            return jsonify({'message': 'Kuis sudah pernah dikerjakan'}), 400
        
        # Buat attempt baru
        attempt = QuizAttempt(
            quiz_id=quiz.id,
            student_id=student.id,
            started_at=datetime.utcnow()
        )
        
        db.session.add(attempt)
        db.session.commit()
        
        # Ambil soal-soal kuis
        questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).order_by(QuizQuestion.order).all()
        questions_data = []
        
        for question in questions:
            question_data = question.to_dict()
            # Jangan kirim correct_answer ke frontend
            del question_data['correct_answer']
            questions_data.append(question_data)
        
        return jsonify({
            'message': 'Kuis dimulai',
            'attempt': attempt.to_dict(),
            'quiz': quiz.to_dict(),
            'questions': questions_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@student_bp.route('/quizzes/<quiz_id>/submit-answer', methods=['POST'])
@student_required
def submit_quiz_answer(quiz_id):
    """Mengirim jawaban kuis"""
    try:
        current_user = get_current_user()
        student = current_user.student
        
        if not student:
            return jsonify({'message': 'Data siswa tidak ditemukan'}), 404
        
        # Cek attempt yang sedang berjalan
        attempt = QuizAttempt.query.filter_by(
            quiz_id=quiz_id,
            student_id=student.id,
            finished_at=None
        ).first()
        
        if not attempt:
            return jsonify({'message': 'Tidak ada kuis yang sedang dikerjakan'}), 400
        
        data = request.get_json()
        if not data or not data.get('question_id') or not data.get('answer'):
            return jsonify({'message': 'Data jawaban tidak lengkap'}), 400
        
        question = QuizQuestion.query.get(data['question_id'])
        if not question or question.quiz_id != quiz_id:
            return jsonify({'message': 'Soal tidak ditemukan'}), 404
        
        # Cek apakah sudah pernah menjawab soal ini
        existing_answer = QuizAnswer.query.filter_by(
            attempt_id=attempt.id,
            question_id=question.id
        ).first()
        
        if existing_answer:
            return jsonify({'message': 'Soal sudah pernah dijawab'}), 400
        
        # Evaluasi jawaban
        is_correct = str(data['answer']).strip().lower() == str(question.correct_answer).strip().lower()
        
        # Simpan jawaban
        answer = QuizAnswer(
            attempt_id=attempt.id,
            question_id=question.id,
            student_answer=str(data['answer']),
            is_correct=is_correct,
            answered_at=datetime.utcnow()
        )
        
        db.session.add(answer)
        db.session.commit()
        
        return jsonify({
            'message': 'Jawaban berhasil disimpan',
            'is_correct': is_correct
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@student_bp.route('/quizzes/<quiz_id>/finish', methods=['POST'])
@student_required
def finish_quiz(quiz_id):
    """Menyelesaikan kuis"""
    try:
        current_user = get_current_user()
        student = current_user.student
        
        if not student:
            return jsonify({'message': 'Data siswa tidak ditemukan'}), 404
        
        # Cek attempt yang sedang berjalan
        attempt = QuizAttempt.query.filter_by(
            quiz_id=quiz_id,
            student_id=student.id,
            finished_at=None
        ).first()
        
        if not attempt:
            return jsonify({'message': 'Tidak ada kuis yang sedang dikerjakan'}), 400
        
        # Hitung skor
        total_questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).count()
        correct_answers = QuizAnswer.query.filter_by(
            attempt_id=attempt.id,
            is_correct=True
        ).count()
        
        score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Update attempt
        attempt.finished_at = datetime.utcnow()
        attempt.score = score
        
        db.session.commit()
        
        return jsonify({
            'message': 'Kuis selesai',
            'attempt': attempt.to_dict(),
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@student_bp.route('/grades', methods=['GET'])
@student_required
def get_grades():
    """Melihat nilai siswa"""
    try:
        current_user = get_current_user()
        student = current_user.student
        
        if not student:
            return jsonify({'message': 'Data siswa tidak ditemukan'}), 404
        
        grades = Grade.query.filter_by(student_id=student.id).all()
        
        return jsonify({'grades': [grade.to_dict() for grade in grades]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@student_bp.route('/messages', methods=['GET'])
@student_required
def get_messages():
    """Melihat pesan siswa"""
    try:
        current_user = get_current_user()
        student = current_user.student
        
        if not student:
            return jsonify({'message': 'Data siswa tidak ditemukan'}), 404
        
        # Ambil pesan pribadi dan pesan grup kelas
        messages = Message.query.filter(
            (Message.receiver_id == current_user.id) |
            (Message.rombel_id == student.rombel_id)
        ).order_by(Message.sent_at.desc()).all()
        
        return jsonify({'messages': [message.to_dict() for message in messages]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@student_bp.route('/messages', methods=['POST'])
@student_required
def send_message():
    """Mengirim pesan"""
    try:
        current_user = get_current_user()
        student = current_user.student
        
        if not student:
            return jsonify({'message': 'Data siswa tidak ditemukan'}), 404
        
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

