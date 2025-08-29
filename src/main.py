import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Import models dan routes
from src.models.models import db, User, Admin, UserRole
from src.utils.auth import jwt, hash_password
from src.routes.auth import auth_bp
from src.routes.admin import admin_bp
from src.routes.student import student_bp
from src.routes.teacher import teacher_bp
from src.routes.parent import parent_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Konfigurasi aplikasi
app.config['SECRET_KEY'] = 'sekune-secret-key-2024-very-secure'
app.config['JWT_SECRET_KEY'] = 'sekune-jwt-secret-key-2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Konfigurasi database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi ekstensi
CORS(app, origins="*")  # Izinkan semua origin untuk development
jwt.init_app(app)
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(student_bp, url_prefix='/api/student')
app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
app.register_blueprint(parent_bp, url_prefix='/api/parent')

# Inisialisasi database dan data default
with app.app_context():
    db.create_all()
    
    # Buat admin default jika belum ada
    admin_user = User.query.filter_by(email='admin@sekune.com').first()
    if not admin_user:
        admin_user = User(
            email='admin@sekune.com',
            password=hash_password('admin123'),
            role=UserRole.ADMIN
        )
        db.session.add(admin_user)
        db.session.flush()
        
        admin_profile = Admin(
            user_id=admin_user.id,
            name='Administrator SeKuNe'
        )
        db.session.add(admin_profile)
        db.session.commit()
        
        print("Admin default berhasil dibuat:")
        print("Email: admin@sekune.com")
        print("Password: admin123")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint tidak ditemukan'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Terjadi kesalahan server internal'}), 500

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': 'Token sudah kadaluarsa'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'message': 'Token tidak valid'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'message': 'Token diperlukan untuk mengakses endpoint ini'}), 401

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'OK',
        'message': 'SeKuNe Backend API berjalan dengan baik',
        'version': '1.0.0'
    }), 200

# Serve frontend files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return jsonify({'message': 'Frontend belum dikonfigurasi'}), 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'SeKuNe Backend API',
                'endpoints': {
                    'health': '/api/health',
                    'auth': '/api/auth/*',
                    'admin': '/api/admin/*',
                    'student': '/api/student/*',
                    'teacher': '/api/teacher/*',
                    'parent': '/api/parent/*'
                }
            }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
