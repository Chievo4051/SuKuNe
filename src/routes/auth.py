from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.models import User, Student, Teacher, Parent, Admin, db
from src.utils.auth import check_password, create_token, get_current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email dan password harus diisi'}), 400
        
        email = data['email']
        password = data['password']
        
        # Cari user berdasarkan email
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password(user.password, password):
            return jsonify({'message': 'Email atau password salah'}), 401
        
        # Buat token
        token = create_token(user.id)
        
        # Dapatkan data profil berdasarkan role
        profile_data = {}
        if user.role.value == 'siswa' and user.student:
            profile_data = user.student.to_dict()
        elif user.role.value == 'guru' and user.teacher:
            profile_data = user.teacher.to_dict()
        elif user.role.value == 'orang_tua' and user.parent:
            profile_data = user.parent.to_dict()
        elif user.role.value == 'admin' and user.admin:
            profile_data = user.admin.to_dict()
        
        return jsonify({
            'message': 'Login berhasil',
            'token': token,
            'user': user.to_dict(),
            'profile': profile_data
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    """Mendapatkan profil user yang sedang login"""
    try:
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({'message': 'User tidak ditemukan'}), 404
        
        # Dapatkan data profil berdasarkan role
        profile_data = {}
        if current_user.role.value == 'siswa' and current_user.student:
            profile_data = current_user.student.to_dict()
        elif current_user.role.value == 'guru' and current_user.teacher:
            profile_data = current_user.teacher.to_dict()
        elif current_user.role.value == 'orang_tua' and current_user.parent:
            profile_data = current_user.parent.to_dict()
        elif current_user.role.value == 'admin' and current_user.admin:
            profile_data = current_user.admin.to_dict()
        
        return jsonify({
            'user': current_user.to_dict(),
            'profile': profile_data
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endpoint (untuk keperluan frontend, JWT stateless)"""
    return jsonify({'message': 'Logout berhasil'}), 200

