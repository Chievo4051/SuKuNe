from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import jsonify
from src.models.models import User, db

jwt = JWTManager()

def hash_password(password):
    """Hash password menggunakan werkzeug"""
    return generate_password_hash(password)

def check_password(hashed_password, password):
    """Verifikasi password"""
    return check_password_hash(hashed_password, password)

def create_token(user_id):
    """Membuat JWT token"""
    return create_access_token(identity=user_id)

def get_current_user():
    """Mendapatkan user yang sedang login"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)

def role_required(allowed_roles):
    """Decorator untuk membatasi akses berdasarkan role"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if not current_user or current_user.role.value not in allowed_roles:
                return jsonify({'message': 'Akses ditolak'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator khusus untuk admin"""
    return role_required(['admin'])(f)

def teacher_required(f):
    """Decorator khusus untuk guru"""
    return role_required(['guru'])(f)

def student_required(f):
    """Decorator khusus untuk siswa"""
    return role_required(['siswa'])(f)

def parent_required(f):
    """Decorator khusus untuk orang tua"""
    return role_required(['orang_tua'])(f)

