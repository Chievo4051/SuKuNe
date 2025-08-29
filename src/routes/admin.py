from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.models import (
    User, Student, Teacher, Parent, Admin, Rombel, Subject, SchoolSettings, 
    UserRole, db
)
from src.utils.auth import admin_required, hash_password
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """Mendaftarkan pengguna baru (siswa, guru, orang tua)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Data tidak boleh kosong'}), 400
        
        # Validasi data berdasarkan tipe user
        user_type = data.get('type')  # 'siswa_orang_tua' atau 'guru'
        
        if user_type == 'siswa_orang_tua':
            # Validasi data siswa dan orang tua
            required_fields = ['nama_siswa', 'nickname', 'email_siswa', 'nama_orang_tua', 
                             'email_orang_tua', 'password_siswa', 'password_orang_tua', 'rombel_id']
            
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'message': f'Field {field} harus diisi'}), 400
            
            # Cek apakah email sudah ada
            if User.query.filter_by(email=data['email_siswa']).first():
                return jsonify({'message': 'Email siswa sudah terdaftar'}), 400
            
            if User.query.filter_by(email=data['email_orang_tua']).first():
                return jsonify({'message': 'Email orang tua sudah terdaftar'}), 400
            
            # Cek apakah rombel ada
            rombel = Rombel.query.get(data['rombel_id'])
            if not rombel:
                return jsonify({'message': 'Rombel tidak ditemukan'}), 404
            
            # Buat user orang tua terlebih dahulu
            parent_user = User(
                email=data['email_orang_tua'],
                password=hash_password(data['password_orang_tua']),
                role=UserRole.ORANG_TUA
            )
            db.session.add(parent_user)
            db.session.flush()  # Untuk mendapatkan ID
            
            # Buat profil orang tua
            parent = Parent(
                user_id=parent_user.id,
                name=data['nama_orang_tua']
            )
            db.session.add(parent)
            db.session.flush()
            
            # Buat user siswa
            student_user = User(
                email=data['email_siswa'],
                password=hash_password(data['password_siswa']),
                role=UserRole.SISWA
            )
            db.session.add(student_user)
            db.session.flush()
            
            # Buat profil siswa
            student = Student(
                user_id=student_user.id,
                name=data['nama_siswa'],
                nickname=data['nickname'],
                parent_id=parent.id,
                rombel_id=data['rombel_id']
            )
            db.session.add(student)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Siswa dan orang tua berhasil didaftarkan',
                'student': student.to_dict(),
                'parent': parent.to_dict()
            }), 201
            
        elif user_type == 'guru':
            # Validasi data guru
            required_fields = ['nama_guru', 'email_guru', 'password']
            
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'message': f'Field {field} harus diisi'}), 400
            
            # Cek apakah email sudah ada
            if User.query.filter_by(email=data['email_guru']).first():
                return jsonify({'message': 'Email guru sudah terdaftar'}), 400
            
            # Buat user guru
            teacher_user = User(
                email=data['email_guru'],
                password=hash_password(data['password']),
                role=UserRole.GURU
            )
            db.session.add(teacher_user)
            db.session.flush()
            
            # Buat profil guru
            teacher = Teacher(
                user_id=teacher_user.id,
                name=data['nama_guru'],
                is_wali_kelas=data.get('is_wali_kelas', False)
            )
            db.session.add(teacher)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Guru berhasil didaftarkan',
                'teacher': teacher.to_dict()
            }), 201
            
        else:
            return jsonify({'message': 'Tipe user tidak valid'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Melihat daftar semua pengguna"""
    try:
        users = User.query.all()
        users_data = []
        
        for user in users:
            user_data = user.to_dict()
            
            # Tambahkan data profil
            if user.role.value == 'siswa' and user.student:
                user_data['profile'] = user.student.to_dict()
            elif user.role.value == 'guru' and user.teacher:
                user_data['profile'] = user.teacher.to_dict()
            elif user.role.value == 'orang_tua' and user.parent:
                user_data['profile'] = user.parent.to_dict()
            elif user.role.value == 'admin' and user.admin:
                user_data['profile'] = user.admin.to_dict()
            
            users_data.append(user_data)
        
        return jsonify({'users': users_data}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@admin_bp.route('/users/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Mengelola data dan status akun pengguna"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User tidak ditemukan'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Data tidak boleh kosong'}), 400
        
        # Update data user
        if 'email' in data:
            # Cek apakah email baru sudah digunakan
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'message': 'Email sudah digunakan'}), 400
            user.email = data['email']
        
        if 'password' in data:
            user.password = hash_password(data['password'])
        
        # Update data profil berdasarkan role
        if user.role.value == 'siswa' and user.student:
            if 'name' in data:
                user.student.name = data['name']
            if 'nickname' in data:
                user.student.nickname = data['nickname']
            if 'rombel_id' in data:
                rombel = Rombel.query.get(data['rombel_id'])
                if not rombel:
                    return jsonify({'message': 'Rombel tidak ditemukan'}), 404
                user.student.rombel_id = data['rombel_id']
                
        elif user.role.value == 'guru' and user.teacher:
            if 'name' in data:
                user.teacher.name = data['name']
            if 'is_wali_kelas' in data:
                user.teacher.is_wali_kelas = data['is_wali_kelas']
                
        elif user.role.value == 'orang_tua' and user.parent:
            if 'name' in data:
                user.parent.name = data['name']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Data user berhasil diupdate',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@admin_bp.route('/rombels', methods=['POST'])
@admin_required
def create_rombel():
    """Menambah rombel baru"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'Nama rombel harus diisi'}), 400
        
        # Cek apakah nama rombel sudah ada
        if Rombel.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'Nama rombel sudah ada'}), 400
        
        # Validasi wali kelas jika ada
        wali_kelas_id = data.get('wali_kelas_id')
        if wali_kelas_id:
            teacher = Teacher.query.get(wali_kelas_id)
            if not teacher:
                return jsonify({'message': 'Guru tidak ditemukan'}), 404
        
        rombel = Rombel(
            name=data['name'],
            wali_kelas_id=wali_kelas_id
        )
        
        db.session.add(rombel)
        db.session.commit()
        
        return jsonify({
            'message': 'Rombel berhasil dibuat',
            'rombel': rombel.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@admin_bp.route('/rombels', methods=['GET'])
@admin_required
def get_rombels():
    """Melihat daftar rombel"""
    try:
        rombels = Rombel.query.all()
        return jsonify({'rombels': [rombel.to_dict() for rombel in rombels]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@admin_bp.route('/rombels/<rombel_id>', methods=['PUT'])
@admin_required
def update_rombel(rombel_id):
    """Update rombel"""
    try:
        rombel = Rombel.query.get(rombel_id)
        if not rombel:
            return jsonify({'message': 'Rombel tidak ditemukan'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Data tidak boleh kosong'}), 400
        
        if 'name' in data:
            # Cek apakah nama baru sudah digunakan
            existing_rombel = Rombel.query.filter_by(name=data['name']).first()
            if existing_rombel and existing_rombel.id != rombel.id:
                return jsonify({'message': 'Nama rombel sudah digunakan'}), 400
            rombel.name = data['name']
        
        if 'wali_kelas_id' in data:
            if data['wali_kelas_id']:
                teacher = Teacher.query.get(data['wali_kelas_id'])
                if not teacher:
                    return jsonify({'message': 'Guru tidak ditemukan'}), 404
            rombel.wali_kelas_id = data['wali_kelas_id']
        
        rombel.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Rombel berhasil diupdate',
            'rombel': rombel.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@admin_bp.route('/rombels/<rombel_id>', methods=['DELETE'])
@admin_required
def delete_rombel(rombel_id):
    """Hapus rombel"""
    try:
        rombel = Rombel.query.get(rombel_id)
        if not rombel:
            return jsonify({'message': 'Rombel tidak ditemukan'}), 404
        
        # Cek apakah ada siswa di rombel ini
        if rombel.students:
            return jsonify({'message': 'Tidak dapat menghapus rombel yang masih memiliki siswa'}), 400
        
        db.session.delete(rombel)
        db.session.commit()
        
        return jsonify({'message': 'Rombel berhasil dihapus'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@admin_bp.route('/school-settings', methods=['GET'])
@admin_required
def get_school_settings():
    """Mendapatkan pengaturan sekolah"""
    try:
        settings = SchoolSettings.query.first()
        if not settings:
            # Buat pengaturan default jika belum ada
            settings = SchoolSettings(
                school_name='SeKuNe - Sekolah Ku Online',
                school_logo_url=None
            )
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({'settings': settings.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@admin_bp.route('/school-settings', methods=['PUT'])
@admin_required
def update_school_settings():
    """Mengubah identitas sekolah"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Data tidak boleh kosong'}), 400
        
        settings = SchoolSettings.query.first()
        if not settings:
            settings = SchoolSettings()
            db.session.add(settings)
        
        if 'school_name' in data:
            settings.school_name = data['school_name']
        
        if 'school_logo_url' in data:
            settings.school_logo_url = data['school_logo_url']
        
        settings.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Pengaturan sekolah berhasil diupdate',
            'settings': settings.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@admin_bp.route('/subjects', methods=['POST'])
@admin_required
def create_subject():
    """Menambah mata pelajaran baru"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'Nama mata pelajaran harus diisi'}), 400
        
        # Cek apakah nama mata pelajaran sudah ada
        if Subject.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'Nama mata pelajaran sudah ada'}), 400
        
        subject = Subject(name=data['name'])
        db.session.add(subject)
        db.session.commit()
        
        return jsonify({
            'message': 'Mata pelajaran berhasil dibuat',
            'subject': subject.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@admin_bp.route('/subjects', methods=['GET'])
@admin_required
def get_subjects():
    """Melihat daftar mata pelajaran"""
    try:
        subjects = Subject.query.all()
        return jsonify({'subjects': [subject.to_dict() for subject in subjects]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

