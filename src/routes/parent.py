from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.models import Grade, Message, Student, Parent, db
from src.utils.auth import parent_required, get_current_user
from datetime import datetime
from sqlalchemy import func

parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/children', methods=['GET'])
@parent_required
def get_children():
    """Melihat daftar anak"""
    try:
        current_user = get_current_user()
        parent = current_user.parent
        
        if not parent:
            return jsonify({'message': 'Data orang tua tidak ditemukan'}), 404
        
        children = Student.query.filter_by(parent_id=parent.id).all()
        
        return jsonify({'children': [child.to_dict() for child in children]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@parent_bp.route('/children/<student_id>/grades', methods=['GET'])
@parent_required
def get_child_grades(student_id):
    """Melihat nilai anak"""
    try:
        current_user = get_current_user()
        parent = current_user.parent
        
        if not parent:
            return jsonify({'message': 'Data orang tua tidak ditemukan'}), 404
        
        # Pastikan siswa adalah anak dari orang tua ini
        student = Student.query.filter_by(id=student_id, parent_id=parent.id).first()
        if not student:
            return jsonify({'message': 'Siswa tidak ditemukan atau bukan anak Anda'}), 404
        
        # Ambil semua nilai anak
        grades = Grade.query.filter_by(student_id=student_id).order_by(Grade.graded_at.desc()).all()
        
        # Hitung statistik nilai
        if grades:
            grade_values = [float(grade.value) for grade in grades]
            average_grade = sum(grade_values) / len(grade_values)
            highest_grade = max(grade_values)
            lowest_grade = min(grade_values)
        else:
            average_grade = 0
            highest_grade = 0
            lowest_grade = 0
        
        # Grup nilai berdasarkan mata pelajaran (jika ada)
        grades_by_subject = {}
        for grade in grades:
            if grade.subject_id:
                subject_name = grade.subject.name if grade.subject else 'Tidak diketahui'
                if subject_name not in grades_by_subject:
                    grades_by_subject[subject_name] = []
                grades_by_subject[subject_name].append(grade.to_dict())
        
        # Hitung rata-rata per mata pelajaran
        subject_averages = {}
        for subject, subject_grades in grades_by_subject.items():
            subject_values = [float(g['value']) for g in subject_grades]
            subject_averages[subject] = sum(subject_values) / len(subject_values)
        
        return jsonify({
            'student': student.to_dict(),
            'grades': [grade.to_dict() for grade in grades],
            'statistics': {
                'average_grade': round(average_grade, 2),
                'highest_grade': highest_grade,
                'lowest_grade': lowest_grade,
                'total_grades': len(grades)
            },
            'grades_by_subject': grades_by_subject,
            'subject_averages': {k: round(v, 2) for k, v in subject_averages.items()}
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@parent_bp.route('/children/<student_id>/grades/summary', methods=['GET'])
@parent_required
def get_child_grades_summary(student_id):
    """Melihat ringkasan nilai anak (untuk tampilan grafis)"""
    try:
        current_user = get_current_user()
        parent = current_user.parent
        
        if not parent:
            return jsonify({'message': 'Data orang tua tidak ditemukan'}), 404
        
        # Pastikan siswa adalah anak dari orang tua ini
        student = Student.query.filter_by(id=student_id, parent_id=parent.id).first()
        if not student:
            return jsonify({'message': 'Siswa tidak ditemukan atau bukan anak Anda'}), 404
        
        # Ambil rata-rata nilai per bulan (untuk grafik perkembangan)
        monthly_averages = db.session.query(
            func.strftime('%Y-%m', Grade.graded_at).label('month'),
            func.avg(Grade.value).label('average')
        ).filter_by(student_id=student_id).group_by(
            func.strftime('%Y-%m', Grade.graded_at)
        ).order_by('month').all()
        
        # Format data untuk grafik
        chart_data = []
        for month, average in monthly_averages:
            chart_data.append({
                'month': month,
                'average': round(float(average), 2)
            })
        
        # Ambil rata-rata per mata pelajaran
        subject_averages = db.session.query(
            Grade.subject_id,
            func.avg(Grade.value).label('average')
        ).filter_by(student_id=student_id).filter(
            Grade.subject_id.isnot(None)
        ).group_by(Grade.subject_id).all()
        
        subject_data = []
        for subject_id, average in subject_averages:
            from src.models.models import Subject
            subject = Subject.query.get(subject_id)
            subject_data.append({
                'subject_name': subject.name if subject else 'Tidak diketahui',
                'average': round(float(average), 2)
            })
        
        return jsonify({
            'student': student.to_dict(),
            'monthly_progress': chart_data,
            'subject_averages': subject_data
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@parent_bp.route('/messages', methods=['GET'])
@parent_required
def get_messages():
    """Melihat pesan orang tua"""
    try:
        current_user = get_current_user()
        
        # Ambil pesan yang diterima orang tua
        messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.sent_at.desc()).all()
        
        return jsonify({'messages': [message.to_dict() for message in messages]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@parent_bp.route('/messages', methods=['POST'])
@parent_required
def send_message():
    """Mengirim pesan ke wali kelas"""
    try:
        current_user = get_current_user()
        parent = current_user.parent
        
        if not parent:
            return jsonify({'message': 'Data orang tua tidak ditemukan'}), 404
        
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'message': 'Konten pesan harus diisi'}), 400
        
        # Validasi receiver (harus wali kelas atau guru)
        receiver_id = data.get('receiver_id')
        if receiver_id:
            from src.models.models import User, Teacher
            receiver = User.query.get(receiver_id)
            if not receiver or receiver.role.value != 'guru':
                return jsonify({'message': 'Penerima pesan harus guru'}), 400
        
        message = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            rombel_id=data.get('rombel_id'),  # Untuk grup chat dengan wali kelas
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

@parent_bp.route('/children/<student_id>/wali-kelas', methods=['GET'])
@parent_required
def get_child_wali_kelas(student_id):
    """Mendapatkan informasi wali kelas anak"""
    try:
        current_user = get_current_user()
        parent = current_user.parent
        
        if not parent:
            return jsonify({'message': 'Data orang tua tidak ditemukan'}), 404
        
        # Pastikan siswa adalah anak dari orang tua ini
        student = Student.query.filter_by(id=student_id, parent_id=parent.id).first()
        if not student:
            return jsonify({'message': 'Siswa tidak ditemukan atau bukan anak Anda'}), 404
        
        # Ambil informasi wali kelas
        rombel = student.rombel
        wali_kelas = rombel.wali_kelas if rombel else None
        
        if not wali_kelas:
            return jsonify({'message': 'Wali kelas belum ditentukan'}), 404
        
        return jsonify({
            'student': student.to_dict(),
            'rombel': rombel.to_dict(),
            'wali_kelas': wali_kelas.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@parent_bp.route('/rombel-messages/<rombel_id>', methods=['GET'])
@parent_required
def get_rombel_messages(rombel_id):
    """Melihat pesan grup kelas (forum orang tua dengan wali kelas)"""
    try:
        current_user = get_current_user()
        parent = current_user.parent
        
        if not parent:
            return jsonify({'message': 'Data orang tua tidak ditemukan'}), 404
        
        # Pastikan orang tua memiliki anak di rombel ini
        child_in_rombel = Student.query.filter_by(parent_id=parent.id, rombel_id=rombel_id).first()
        if not child_in_rombel:
            return jsonify({'message': 'Anda tidak memiliki anak di rombel ini'}), 403
        
        # Ambil pesan grup rombel
        messages = Message.query.filter_by(rombel_id=rombel_id).order_by(Message.sent_at.desc()).all()
        
        return jsonify({
            'rombel_id': rombel_id,
            'messages': [message.to_dict() for message in messages]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

