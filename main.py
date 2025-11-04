"""
Login & Register API
Flask API untuk autentikasi user dengan MD5 password hashing + Stateless Steganography
"""

from flask import Flask, request, jsonify, send_file
from connection import get_db_connection
from config import config
from auth import AuthService, hash_password_md5, validate_email
from message_service import MessageService
import traceback
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret_key

# File Upload Configuration
UPLOAD_FOLDER = 'uploads/message_attachments'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp',  # Images
    'pdf', 'doc', 'docx', 'txt', 'rtf',  # Documents
    'zip', 'rar', '7z',  # Archives
    'mp3', 'mp4', 'avi', 'mov',  # Media
    'xlsx', 'xls', 'csv'  # Spreadsheets
}

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Inisialisasi database connection
db = get_db_connection(**config.get_db_config())

# Inisialisasi Auth Service
auth_service = AuthService(db)

# Inisialisasi Message Service
message_service = MessageService(db)


# Force commit after every request
# @app.after_request
# def after_request(response):
#     """Force commit setelah setiap request"""
#     try:
#         if db.connection and db.connection.is_connected():
#             # Force commit untuk ensure semua changes tersimpan
#             db.connection.commit()
#     except Exception as e:
#         print(f"⚠️ After request commit error: {e}")
#     return response


@app.route('/')
def index():
    """Homepage API"""
    return jsonify({
        'message': 'Kripto App API - MD5 + Steganography + File Encryption + Super Encrypt',
        'version': '4.1',
        'security': 'MD5 Password Hashing',
        'endpoints': {
            # User Management
            'users': '/api/users',
            'user_by_id': '/api/users/<id>',
            'login': '/api/login',
            'register': '/api/register',
            'change_password': '/api/change-password',
            # 'test_db': '/api/test-db',
            # 'hash_password': '/api/hash-password',
            # Steganography Stateless API (No Database!)
            'stego_encode': '/api/stego/encode',  # Upload gambar + pesan → return gambar hasil
            'stego_decode': '/api/stego/decode',  # Upload gambar → return pesan
            # File Encryption Stateless API (No Database!)
            'file_encrypt': '/api/file/encrypt',  # Upload file + password → return encrypted file
            'file_decrypt': '/api/file/decrypt',  # Upload encrypted file + password → return original file
            # Super Encrypt Stateless API (No Database!)
            'super_encrypt': '/api/super-encrypt',  # Encrypt text: Caesar → Vigenere → DES
            'super_decrypt': '/api/super-decrypt',  # Decrypt text: DES → Vigenere → Caesar
            # Messaging API
            'send_message': '/api/messages/send',  # POST - Kirim pesan (text + optional files)
            'inbox': '/api/messages/inbox',  # GET - Pesan masuk
            'sent_messages': '/api/messages/sent',  # GET - Pesan terkirim
            'message_detail': '/api/messages/<id>',  # GET - Detail pesan
            'delete_message': '/api/messages/<id>',  # DELETE - Hapus pesan
            # 'conversation': '/api/messages/conversation/<user_id>',  # GET - Percakapan dengan user
            # 'search_messages': '/api/messages/search',  # GET - Cari pesan
            'download_attachment': '/api/messages/attachments/<id>',  # GET - Download file attachment
            # Test
            'test': '/tes/<name>'
        }
    })


# @app.route('/tes/<koneksi>')
# def test_endpoint(koneksi):
#     """Test endpoint"""
#     return jsonify({
#         'message': f"Hello, {koneksi}!",
#         'status': 'success'
#     })


# ==================== STEGANOGRAPHY STATELESS API ====================
# No Database! No File Storage! Pure Processing Only!

@app.route('/api/stego/encode', methods=['POST'])
def stego_encode_stateless():
    """
    🎯 STATELESS ENCODE - Encode message ke gambar tanpa save ke database/server
    
    User upload gambar + pesan → return gambar hasil (base64) → user download sendiri
    
    Request Body:
    {
        "image_data": "base64_encoded_image",
        "secret_message": "pesan rahasia"
    }
    
    Response:
    {
        "success": true,
        "message": "Pesan berhasil disembunyikan dalam gambar",
        "data": {
            "encoded_image": "base64_encoded_result_image",
            "original_size": 1920x1080,
            "message_length": 18,
            "capacity_used": "0.002%",
            "format": "PNG"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validasi input
        if not data or not data.get('image_data') or not data.get('secret_message'):
            return jsonify({
                'success': False,
                'message': 'image_data dan secret_message harus diisi'
            }), 400
        
        image_base64 = data['image_data']
        secret_message = data['secret_message']
        
        # Clean base64 string
        if isinstance(image_base64, str):
            if 'base64,' in image_base64:
                image_base64 = image_base64.split('base64,')[1]
            image_base64 = image_base64.strip().replace('\n', '').replace('\r', '')
        
        print(f"📝 Encoding message ({len(secret_message)} chars) into image...")
        
        # Import steganography
        from utils.steganography import Steganography
        stego = Steganography()
        
        # Check capacity
        capacity_info = stego.check_capacity(image_base64)
        
        if len(secret_message) > capacity_info['max_characters']:
            return jsonify({
                'success': False,
                'message': f'Pesan terlalu panjang! Maksimal {capacity_info["max_characters"]} karakter, pesan kamu {len(secret_message)} karakter',
                'image_info': capacity_info
            }), 400
        
        # Encode message
        encoded_image_base64 = stego.encode_message(image_base64, secret_message)
        
        # Calculate capacity usage
        capacity_used_percent = (len(secret_message) / capacity_info['max_characters']) * 100
        
        print(f"✅ Message encoded successfully!")
        print(f"📊 Capacity used: {capacity_used_percent:.3f}%")
        
        return jsonify({
            'success': True,
            'message': 'Pesan berhasil disembunyikan dalam gambar',
            'data': {
                'encoded_image': encoded_image_base64,  # Base64 gambar hasil
                'image_info': {
                    'width': capacity_info['width'],
                    'height': capacity_info['height'],
                    'total_pixels': capacity_info['total_pixels'],
                    'max_capacity': capacity_info['max_characters']
                },
                'message_length': len(secret_message),
                'capacity_used_percent': round(capacity_used_percent, 3),
                'format': 'PNG',
                'note': 'Download gambar dengan decode base64 ke file PNG'
            }
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/stego/decode', methods=['POST'])
def stego_decode_stateless():
    """
    🔓 STATELESS DECODE - Decode message dari gambar tanpa save ke database
    
    User upload gambar steganografi → return pesan rahasia
    
    Request Body:
    {
        "image_data": "base64_encoded_stego_image"
    }
    
    Response:
    {
        "success": true,
        "message": "Pesan berhasil diekstrak",
        "data": {
            "secret_message": "pesan rahasia",
            "message_length": 18,
            "image_info": {
                "width": 1920,
                "height": 1080
            }
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validasi input
        if not data or not data.get('image_data'):
            return jsonify({
                'success': False,
                'message': 'image_data harus diisi'
            }), 400
        
        image_base64 = data['image_data']
        
        # Clean base64 string
        if isinstance(image_base64, str):
            if 'base64,' in image_base64:
                image_base64 = image_base64.split('base64,')[1]
            image_base64 = image_base64.strip().replace('\n', '').replace('\r', '')
        
        print(f"🔓 Decoding message from uploaded image...")
        
        # Import steganography
        from utils.steganography import Steganography
        stego = Steganography()
        
        # Get image info
        capacity_info = stego.check_capacity(image_base64)
        
        # Decode message
        secret_message = stego.decode_message(image_base64)
        
        print(f"✅ Message decoded successfully! Length: {len(secret_message)}")
        
        return jsonify({
            'success': True,
            'message': 'Pesan berhasil diekstrak',
            'data': {
                'secret_message': secret_message,
                'message_length': len(secret_message),
                'image_info': {
                    'width': capacity_info['width'],
                    'height': capacity_info['height'],
                    'total_pixels': capacity_info['total_pixels'],
                    'max_capacity': capacity_info['max_characters']
                }
            }
        }), 200
    
    except Exception as e:
        error_message = str(e)
        traceback.print_exc()
        
        # Check jika error karena delimiter tidak ketemu (gambar bukan stego)
        if "Delimiter tidak ditemukan" in error_message:
            return jsonify({
                'success': False,
                'error_type': 'NO_MESSAGE_FOUND',
                'message': 'Gambar ini tidak mengandung pesan steganografi',
                'details': 'Delimiter tidak ditemukan. Pastikan gambar yang diupload sudah di-encode dengan aplikasi ini.',
                'suggestion': 'Gunakan gambar yang sudah di-encode dengan endpoint /api/stego/encode'
            }), 400
        
        # Error lainnya
        return jsonify({
            'success': False,
            'error_type': 'DECODE_ERROR',
            'message': f'Error saat decoding: {error_message}'
        }), 500


@app.route('/api/users', methods=['GET'])
def get_users():
    """Get semua users dari database"""
    try:
        # Query semua users (tanpa password untuk keamanan)
        query = "SELECT id, username, email, created_at FROM users"
        results = db.execute_read_dict(query)
        
        if results:
            return jsonify({
                'success': True,
                'count': len(results),
                'users': results
            })
        else:
            return jsonify({
                'success': True,
                'count': 0,
                'users': []
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """Get user berdasarkan ID"""
    try:
        query = "SELECT id, username, email, created_at FROM users WHERE id = %s"
        result = db.execute_read_dict(query, (user_id,))
        
        if result:
            return jsonify({
                'success': True,
                'user': result[0]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'User tidak ditemukan'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/register', methods=['POST'])
def register():
    """Register user baru dengan MD5 password hashing"""
    try:
        data = request.get_json()
        
        # Validasi input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email dan password harus diisi'
            }), 400
        
        email = data['email']
        password = data['password']
        username = data.get('username')
        
        # Gunakan AuthService untuk register
        result = auth_service.register_user(email, password, username)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/login', methods=['POST'])
def login():
    """Login user dengan MD5 password verification"""
    try:
        data = request.get_json()
        
        # Validasi input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email dan password harus diisi'
            }), 400
        
        email = data['email']
        password = data['password']
        
        # Gunakan AuthService untuk login
        result = auth_service.login_user(email, password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            print('Login gagal:', result['message'])
            return jsonify(result), 401
    
    except Exception as e:
        print(f'Error during login: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


# @app.route('/api/test-db', methods=['GET'])
# def test_database():
#     """Test koneksi database"""
#     try:
#         result = db.execute_read_query("SELECT 1 as test")
#         if result:
#             return jsonify({
#                 'success': True,
#                 'message': 'Koneksi database berhasil',
#                 'database': config.db_database
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'message': 'Koneksi database gagal'
#             }), 500
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Error: {str(e)}'
#         }), 500


@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Change password user"""
    try:
        data = request.get_json()
        
        # Validasi input
        if not data or not data.get('id') or not data.get('old_password') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'message': 'User ID, password lama, dan password baru harus diisi'
            }), 400
        
        user_id = data['id']
        old_password = data['old_password']
        new_password = data['new_password']
        
        # Gunakan AuthService untuk change password
        result = auth_service.change_password(user_id, old_password, new_password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


# @app.route('/api/hash-password', methods=['POST'])
# def hash_password_endpoint():
#     """Endpoint untuk hash password (untuk testing/migration)"""
#     try:
#         data = request.get_json()
        
#         if not data or not data.get('password'):
#             return jsonify({
#                 'success': False,
#                 'message': 'Password harus diisi'
#             }), 400
        
#         password = data['password']
#         hashed = hash_password_md5(password)
        
#         return jsonify({
#             'success': True,
#             'password': password,
#             'md5_hash': hashed
#         })
    
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Error: {str(e)}'
#         }), 500


# ==================== MESSAGING API ====================

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """
    📨 Kirim pesan ke user lain (dengan optional file attachment)
    
    Mode 1 - Text Only (JSON):
    {
        "sender_id": 1,
        "receiver_email": "user@example.com",
        "message_text": "Halo!"
    }
    
    Mode 2 - Text + Files (Form-Data):
    - sender_id: 1
    - receiver_email: user@example.com
    - message_text: Halo, ini ada dokumen
    - files: [file1.pdf, file2.jpg] (optional, multiple files)
    
    Response:
    {
        "success": true,
        "message": "Pesan berhasil dikirim",
        "data": {
            "message_id": 123,
            "receiver_username": "username",
            "sent_at": "2025-11-01T10:30:00",
            "attachments": [...]  // Only if files uploaded
        }
    }
    """
    try:
        # Detect mode: JSON or Form-Data
        if request.is_json:
            # Mode 1: JSON (Text only)
            data = request.get_json()
            files_list = []
        else:
            # Mode 2: Form-Data (Text + optional files)
            data = request.form
            files_list = request.files.getlist('files') if 'files' in request.files else []
        
        # Validasi input
        if not data or not data.get('sender_id') or not data.get('receiver_email') or not data.get('message_text'):
            return jsonify({
                'success': False,
                'message': 'sender_id, receiver_email, dan message_text harus diisi'
            }), 400
        
        sender_id = int(data['sender_id'])
        receiver_email = data['receiver_email']
        message_text = data['message_text']
        
        # Kirim pesan (tanpa attachment dulu)
        result = message_service.send_message(sender_id, receiver_email, message_text)
        
        if not result['success']:
            return jsonify(result), 400
        
        message_id = result['data']['message_id']
        attachments = []
        
        # Process file uploads (if any)
        if files_list:
            for file in files_list:
                if file and file.filename:
                    # Check file extension
                    if not allowed_file(file.filename):
                        continue
                    
                    # Check file size
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > MAX_FILE_SIZE:
                        continue
                    
                    # Generate unique filename
                    original_filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_id = str(uuid.uuid4())[:8]
                    filename = f"{timestamp}_{unique_id}_{original_filename}"
                    
                    # Save file
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    
                    # Determine file type
                    ext = original_filename.rsplit('.', 1)[1].lower()
                    if ext in {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}:
                        file_type = 'image'
                    elif ext in {'pdf', 'doc', 'docx', 'txt', 'rtf'}:
                        file_type = 'document'
                    elif ext in {'zip', 'rar', '7z'}:
                        file_type = 'archive'
                    elif ext in {'mp3', 'mp4', 'avi', 'mov'}:
                        file_type = 'media'
                    elif ext in {'xlsx', 'xls', 'csv'}:
                        file_type = 'spreadsheet'
                    else:
                        file_type = 'other'
                    
                    # Save to database
                    attachment_id = message_service.add_attachment(
                        message_id=message_id,
                        filename=original_filename,
                        file_path=file_path,
                        file_type=file_type,
                        file_size=file_size
                    )
                    
                    attachments.append({
                        'id': attachment_id,
                        'filename': original_filename,
                        'file_type': file_type,
                        'file_size': file_size,
                        'download_url': f'/api/messages/attachments/{attachment_id}'
                    })
        
        # Update response with attachments
        if attachments:
            result['message'] = f"Pesan berhasil dikirim dengan {len(attachments)} attachment"
            result['data']['attachments'] = attachments
        
        return jsonify(result), 201
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/messages/inbox', methods=['GET'])
def get_inbox():
    """
    📬 Ambil pesan masuk (inbox)
    
    Query Parameters:
    - user_id: ID user (required)
    - limit: Jumlah pesan (default: 50)
    - offset: Offset untuk pagination (default: 0)
    
    Example: /api/messages/inbox?user_id=1&limit=20&offset=0
    
    Response:
    {
        "success": true,
        "data": {
            "messages": [...],
            "total": 100,
            "limit": 20,
            "offset": 0
        }
    }
    """
    try:
        user_id = request.args.get('user_id')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'user_id harus diisi'
            }), 400
        
        result = message_service.get_inbox(int(user_id), limit, offset)
        return jsonify(result), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/messages/sent', methods=['GET'])
def get_sent_messages():
    """
    📤 Ambil pesan terkirim (sent messages)
    
    Query Parameters:
    - user_id: ID user (required)
    - limit: Jumlah pesan (default: 50)
    - offset: Offset untuk pagination (default: 0)
    
    Example: /api/messages/sent?user_id=1&limit=20&offset=0
    
    Response:
    {
        "success": true,
        "data": {
            "messages": [...],
            "total": 50,
            "limit": 20,
            "offset": 0
        }
    }
    """
    try:
        user_id = request.args.get('user_id')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'user_id harus diisi'
            }), 400
        
        result = message_service.get_sent_messages(int(user_id), limit, offset)
        return jsonify(result), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/messages/<int:message_id>', methods=['GET'])
def get_message_detail(message_id):
    """
    📄 Ambil detail pesan
    
    Query Parameters:
    - user_id: ID user yang mengakses (required)
    
    Example: /api/messages/123?user_id=1
    
    Response:
    {
        "success": true,
        "data": {
            "id": 123,
            "sender_id": 1,
            "sender_username": "john",
            "receiver_id": 2,
            "receiver_username": "jane",
            "message_text": "Hello!",
            "created_at": "2025-11-01T10:30:00"
        }
    }
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'user_id harus diisi'
            }), 400
        
        result = message_service.get_message_detail(message_id, int(user_id))
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """
    🗑️ Hapus pesan
    
    Request Body:
    {
        "user_id": 1
    }
    
    Response:
    {
        "success": true,
        "message": "Pesan berhasil dihapus"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('user_id'):
            return jsonify({
                'success': False,
                'message': 'user_id harus diisi'
            }), 400
        
        user_id = data['user_id']
        result = message_service.delete_message(message_id, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


# @app.route('/api/messages/conversation/<int:other_user_id>', methods=['GET'])
# def get_conversation(other_user_id):
#     """
#     💬 Ambil percakapan dengan user tertentu
    
#     Query Parameters:
#     - user_id: ID user yang mengakses (required)
#     - limit: Jumlah pesan (default: 50)
    
#     Example: /api/messages/conversation/2?user_id=1&limit=50
    
#     Response:
#     {
#         "success": true,
#         "data": {
#             "other_user": {
#                 "id": 2,
#                 "username": "jane",
#                 "email": "jane@example.com"
#             },
#             "messages": [...],
#             "total": 25
#         }
#     }
#     """
#     try:
#         user_id = request.args.get('user_id')
#         limit = request.args.get('limit', 50, type=int)
        
#         if not user_id:
#             return jsonify({
#                 'success': False,
#                 'message': 'user_id harus diisi'
#             }), 400
        
#         result = message_service.get_conversation(int(user_id), other_user_id, limit)
        
#         if result['success']:
#             return jsonify(result), 200
#         else:
#             return jsonify(result), 404
    
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({
#             'success': False,
#             'message': f'Error: {str(e)}'
#         }), 500


# @app.route('/api/messages/search', methods=['GET'])
# def search_messages():
#     """
#     🔍 Cari pesan berdasarkan keyword
    
#     Query Parameters:
#     - user_id: ID user (required)
#     - keyword: Kata kunci pencarian (required)
#     - limit: Jumlah hasil (default: 50)
    
#     Example: /api/messages/search?user_id=1&keyword=meeting&limit=20
    
#     Response:
#     {
#         "success": true,
#         "data": {
#             "keyword": "meeting",
#             "results": [...],
#             "total": 5
#         }
#     }
#     """
#     try:
#         user_id = request.args.get('user_id')
#         keyword = request.args.get('keyword')
#         limit = request.args.get('limit', 50, type=int)
        
#         if not user_id or not keyword:
#             return jsonify({
#                 'success': False,
#                 'message': 'user_id dan keyword harus diisi'
#             }), 400
        
#         result = message_service.search_messages(int(user_id), keyword, limit)
#         return jsonify(result), 200
    
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify({
#             'success': False,
#             'message': f'Error: {str(e)}'
#         }), 500


@app.route('/api/messages/attachments/<int:attachment_id>', methods=['GET'])
def download_attachment(attachment_id):
    """
    📎 Download file attachment dari pesan
    
    Query Parameters:
    - user_id: ID user yang download (required)
    
    Example: /api/messages/attachments/1?user_id=2
    
    Response:
    - File binary (download)
    
    Error Response:
    {
        "success": false,
        "message": "Attachment tidak ditemukan atau Anda tidak memiliki akses"
    }
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'user_id harus diisi'
            }), 400
        
        # Get attachment info dengan validasi akses
        attachment = message_service.get_attachment(attachment_id, int(user_id))
        
        if not attachment:
            return jsonify({
                'success': False,
                'message': 'Attachment tidak ditemukan atau Anda tidak memiliki akses'
            }), 404
        
        file_path = attachment['file_path']
        filename = attachment['filename']
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': 'File tidak ditemukan di server'
            }), 404
        
        # Send file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


# ==================== FILE ENCRYPTION API (STATELESS) ====================

@app.route('/api/file/encrypt', methods=['POST'])
def file_encrypt_stateless():
    """
    🔐 STATELESS FILE ENCRYPT - Encrypt file tanpa save ke database/server
    
    User upload file (base64) + password → return encrypted file (base64)
    
    Request Body:
    {
        "file_data": "base64_encoded_file",
        "password": "mypassword123",
        "filename": "dokumen.pdf"  (optional)
    }
    
    Response:
    {
        "success": true,
        "message": "File berhasil dienkripsi",
        "data": {
            "encrypted_file": "base64_encrypted_data",
            "original_size": 12345,
            "encrypted_size": 12368,
            "algorithm": "AES-256-CBC",
            "filename": "dokumen.pdf.enc"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validasi input
        if not data or not data.get('file_data') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'file_data dan password harus diisi'
            }), 400
        
        file_base64 = data['file_data']
        password = data['password']
        filename = data.get('filename', 'file.enc')
        
        # Clean base64 string
        if isinstance(file_base64, str):
            if 'base64,' in file_base64:
                file_base64 = file_base64.split('base64,')[1]
            file_base64 = file_base64.strip().replace('\n', '').replace('\r', '')
        
        print(f"🔐 Encrypting file with password...")
        
        # Import AES encryption
        from utils.aes_file_encryption import AESFileEncryption
        import base64
        
        # Decode base64 to bytes
        file_bytes = base64.b64decode(file_base64)
        original_size = len(file_bytes)
        
        # Create AES cipher
        aes = AESFileEncryption(password)
        
        # Encrypt (manual encryption tanpa file)
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad
        
        cipher = AES.new(aes.key, AES.MODE_CBC)
        ciphertext = cipher.encrypt(pad(file_bytes, AES.block_size))
        
        # Combine IV + ciphertext
        encrypted_bytes = cipher.iv + ciphertext
        
        # Encode to base64
        encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        print(f"✅ File encrypted successfully!")
        print(f"📊 Original: {original_size} bytes → Encrypted: {len(encrypted_bytes)} bytes")
        
        return jsonify({
            'success': True,
            'message': 'File berhasil dienkripsi',
            'data': {
                'encrypted_file': encrypted_base64,
                'original_size': original_size,
                'encrypted_size': len(encrypted_bytes),
                'algorithm': 'AES-256-CBC',
                'filename': filename + '.enc',
                'note': 'Download file dengan decode base64 dan simpan dengan extension .enc'
            }
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error_type': 'ENCRYPTION_ERROR',
            'message': f'Error saat enkripsi: {str(e)}'
        }), 500


@app.route('/api/file/decrypt', methods=['POST'])
def file_decrypt_stateless():
    """
    🔓 STATELESS FILE DECRYPT - Decrypt file tanpa save ke database
    
    User upload encrypted file (base64) + password → return original file (base64)
    
    Request Body:
    {
        "file_data": "base64_encrypted_file",
        "password": "mypassword123",
        "filename": "dokumen.pdf.enc"  (optional)
    }
    
    Response:
    {
        "success": true,
        "message": "File berhasil didekripsi",
        "data": {
            "decrypted_file": "base64_original_data",
            "decrypted_size": 12345,
            "algorithm": "AES-256-CBC",
            "filename": "dokumen.pdf"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validasi input
        if not data or not data.get('file_data') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'file_data dan password harus diisi'
            }), 400
        
        file_base64 = data['file_data']
        password = data['password']
        filename = data.get('filename', 'file.enc')
        
        # Clean base64 string
        if isinstance(file_base64, str):
            if 'base64,' in file_base64:
                file_base64 = file_base64.split('base64,')[1]
            file_base64 = file_base64.strip().replace('\n', '').replace('\r', '')
        
        print(f"🔓 Decrypting file with password...")
        
        # Import AES encryption
        from utils.aes_file_encryption import AESFileEncryption
        import base64
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad
        
        # Decode base64 to bytes
        encrypted_bytes = base64.b64decode(file_base64)
        
        # Extract IV (first 16 bytes) and ciphertext
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        
        # Create AES cipher
        aes = AESFileEncryption(password)
        cipher = AES.new(aes.key, AES.MODE_CBC, iv)
        
        # Decrypt
        decrypted_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        # Encode to base64
        decrypted_base64 = base64.b64encode(decrypted_bytes).decode('utf-8')
        
        # Remove .enc extension dari filename
        original_filename = filename[:-4] if filename.endswith('.enc') else filename
        
        print(f"✅ File decrypted successfully!")
        print(f"📊 Decrypted size: {len(decrypted_bytes)} bytes")
        
        return jsonify({
            'success': True,
            'message': 'File berhasil didekripsi',
            'data': {
                'decrypted_file': decrypted_base64,
                'decrypted_size': len(decrypted_bytes),
                'algorithm': 'AES-256-CBC',
                'filename': original_filename,
                'note': 'Download file dengan decode base64'
            }
        }), 200
    
    except ValueError as e:
        # Wrong password or corrupted data
        return jsonify({
            'success': False,
            'error_type': 'WRONG_PASSWORD',
            'message': 'Password salah atau file rusak',
            'details': str(e)
        }), 400
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error_type': 'DECRYPTION_ERROR',
            'message': f'Error saat dekripsi: {str(e)}'
        }), 500


# ==================== SUPER ENCRYPT (STATELESS) ====================

@app.route('/api/super-encrypt', methods=['POST'])
def super_encrypt_text():
    """
    Super Encrypt - Triple layer encryption (Caesar → Vigenere → DES)
    Stateless API - tidak menyimpan ke database
    
    Request Body (JSON):
    {
        "text": "Hello World",
        "caesar_shift": 3,          // Optional, default: 3
        "vigenere_key": "SECRET",   // Optional, default: "KEY"
        "des_key": "mykey123"       // Optional, default: "secret12"
    }
    
    Response:
    {
        "success": true,
        "message": "Text berhasil dienkripsi dengan Super Encrypt",
        "data": {
            "ciphertext": "base64_encrypted_text",
            "iv": "base64_iv",
            "original_length": 11,
            "algorithm": "Caesar → Vigenere → DES"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required field
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'message': 'Field "text" wajib diisi'
            }), 400
        
        text = data['text']
        caesar_shift = data.get('caesar_shift', 3)
        vigenere_key = data.get('vigenere_key', 'KEY')
        des_key = data.get('des_key', 'secret12')
        
        print(f"🔐 Super Encrypting: {text}")
        print(f"   Caesar Shift: {caesar_shift}")
        print(f"   Vigenere Key: {vigenere_key}")
        print(f"   DES Key: {des_key}")
        
        # Import Super Encrypt
        from utils.super_encrypt import SuperEncrypt
        
        # Encrypt with triple layer
        cipher = SuperEncrypt(caesar_shift, vigenere_key, des_key)
        result = cipher.encrypt(text)
        
        print(f"✅ Super Encryption successful!")
        
        return jsonify({
            'success': True,
            'message': 'Text berhasil dienkripsi dengan Super Encrypt',
            'data': {
                'ciphertext': result['ciphertext'],
                'iv': result['iv'],
                'original_length': len(text),
                'algorithm': 'Caesar → Vigenere → DES',
                'note': 'Simpan ciphertext, iv, dan semua keys untuk dekripsi'
            }
        }), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error_type': 'ENCRYPTION_ERROR',
            'message': f'Error saat super encrypt: {str(e)}'
        }), 500


@app.route('/api/super-decrypt', methods=['POST'])
def super_decrypt_text():
    """
    Super Decrypt - Reverse triple layer decryption (DES → Vigenere → Caesar)
    Stateless API - tidak menyimpan ke database
    
    Request Body (JSON):
    {
        "ciphertext": "base64_encrypted_text",
        "iv": "base64_iv",
        "caesar_shift": 3,          // Must match encryption
        "vigenere_key": "SECRET",   // Must match encryption
        "des_key": "mykey123"       // Must match encryption
    }
    
    Response:
    {
        "success": true,
        "message": "Text berhasil didekripsi",
        "data": {
            "plaintext": "Hello World",
            "length": 11,
            "algorithm": "DES → Vigenere → Caesar"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body tidak boleh kosong'
            }), 400
        
        required_fields = ['ciphertext', 'iv', 'caesar_shift', 'vigenere_key', 'des_key']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Field wajib: {", ".join(missing_fields)}'
            }), 400
        
        ciphertext = data['ciphertext']
        iv = data['iv']
        caesar_shift = data['caesar_shift']
        vigenere_key = data['vigenere_key']
        des_key = data['des_key']
        
        print(f"🔓 Super Decrypting...")
        print(f"   Caesar Shift: {caesar_shift}")
        print(f"   Vigenere Key: {vigenere_key}")
        print(f"   DES Key: {des_key}")
        
        # Import Super Encrypt
        from utils.super_encrypt import SuperEncrypt
        
        # Decrypt with triple layer (reverse)
        cipher = SuperEncrypt(caesar_shift, vigenere_key, des_key)
        encrypted_data = {
            'ciphertext': ciphertext,
            'iv': iv
        }
        plaintext = cipher.decrypt(encrypted_data)
        
        print(f"✅ Super Decryption successful!")
        print(f"   Plaintext: {plaintext}")
        
        return jsonify({
            'success': True,
            'message': 'Text berhasil didekripsi',
            'data': {
                'plaintext': plaintext,
                'length': len(plaintext),
                'algorithm': 'DES → Vigenere → Caesar'
            }
        }), 200
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error_type': 'WRONG_KEY',
            'message': 'Key atau password salah',
            'details': str(e)
        }), 400
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error_type': 'DECRYPTION_ERROR',
            'message': f'Error saat super decrypt: {str(e)}'
        }), 500


# ==================== SERVER STARTUP ====================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting Kripto App API Server")
    print("="*50)
    print("📌 Features:")
    print("   - User Authentication (MD5)")
    print("   - Stateless Steganography (LSB)")
    print("   - Stateless File Encryption (AES)")
    print("   - Stateless Super Encrypt (Caesar+Vigenere+DES)")
    print("   - Messaging System (Email-like)")
    config.display_config()
    print("="*50 + "\n")
    
    app.run(
        host=config.flask_host,
        port=config.flask_port,
        debug=config.flask_debug
    )
