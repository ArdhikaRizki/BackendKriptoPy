# MD5 Password Hashing - Kripto App

## 📖 Tentang MD5

**MD5 (Message Digest Algorithm 5)** adalah fungsi hash kriptografi yang menghasilkan nilai hash 128-bit (32 karakter hexadecimal).

### Contoh MD5 Hash:
```
Password: "password123"
MD5 Hash: "482c811da5d5b4bc6d497ffa98491e38"
```

---

## 🚀 Cara Penggunaan

### 1. Import Module

```python
from auth import hash_password_md5, verify_password_md5, AuthService
from connection import get_db_connection
from config import config
```

### 2. Hash Password

```python
# Hash password
password = "password123"
hashed = hash_password_md5(password)
print(hashed)  # Output: 482c811da5d5b4bc6d497ffa98491e38
```

### 3. Verify Password

```python
# Verify password
is_valid = verify_password_md5("password123", hashed)
print(is_valid)  # Output: True

# Wrong password
is_valid = verify_password_md5("wrongpass", hashed)
print(is_valid)  # Output: False
```

### 4. Gunakan AuthService

```python
# Setup database connection
db = get_db_connection(**config.get_db_config())

# Inisialisasi AuthService
auth = AuthService(db)

# Register user
result = auth.register_user("user@example.com", "password123")
print(result)
# {'success': True, 'message': 'Registrasi berhasil', 'username': 'user'}

# Login user
result = auth.login_user("user@example.com", "password123")
print(result)
# {'success': True, 'message': 'Login berhasil', 'user': {...}}
```

---

## 🌐 API Endpoints

### 1. **Register User**
**POST** `/api/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "username": "user"  // optional
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Registrasi berhasil",
  "username": "user"
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "Email sudah terdaftar"
}
```

---

### 2. **Login User**
**POST** `/api/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Login berhasil",
  "user": {
    "id": 1,
    "username": "user",
    "email": "user@example.com"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "Email atau password salah"
}
```

---

### 3. **Change Password**
**POST** `/api/change-password`

**Request Body:**
```json
{
  "user_id": 1,
  "old_password": "password123",
  "new_password": "newpassword456"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Password berhasil diubah"
}
```

---

### 4. **Hash Password (Testing)**
**POST** `/api/hash-password`

**Request Body:**
```json
{
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "password": "password123",
  "md5_hash": "482c811da5d5b4bc6d497ffa98491e38"
}
```

---

## 🧪 Testing dengan cURL

### Register
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"password123\"}"
```

### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"password123\"}"
```

### Hash Password
```bash
curl -X POST http://localhost:5000/api/hash-password \
  -H "Content-Type: application/json" \
  -d "{\"password\":\"password123\"}"
```

---

## 🧪 Testing dengan Python

### Test auth.py

```bash
cd python
python auth.py
```

Output:
```
=== Test MD5 Password Hashing ===

1. Hash Password:
   Password: password123
   MD5 Hash: 482c811da5d5b4bc6d497ffa98491e38

2. Verify Correct Password:
   Result: True

3. Verify Wrong Password:
   Result: False
...
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(32) NOT NULL,  -- MD5 hash = 32 characters
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📝 Validasi

### Email Validation
- Format: `user@domain.com`
- Regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

### Password Validation
- Minimal: 6 karakter
- Maksimal: 100 karakter

---

## ⚠️ Security Notes

### MD5 dalam Konteks Password:

**Kelebihan:**
- ✅ Cepat dan sederhana
- ✅ Menghasilkan hash yang konsisten
- ✅ Cocok untuk pembelajaran kriptografi

**Kekurangan:**
- ⚠️ **Tidak direkomendasikan untuk production** (rentan terhadap rainbow table attacks)
- ⚠️ Tidak ada salt (password yang sama = hash yang sama)
- ⚠️ Sudah dianggap tidak aman untuk password hashing

### Rekomendasi untuk Production:
Gunakan algoritma modern seperti:
- **bcrypt** (recommended)
- **Argon2**
- **PBKDF2**

Contoh dengan bcrypt:
```python
import bcrypt

# Hash
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Verify
bcrypt.checkpw(password.encode(), hashed)
```

---

## 🔄 Migration dari Plaintext ke MD5

Jika Anda memiliki password plaintext di database dan ingin migrasi ke MD5:

```python
from connection import get_db_connection
from auth import hash_password_md5
from config import config

# Connect to database
db = get_db_connection(**config.get_db_config())

# Get all users
users = db.execute_read_dict("SELECT id, password FROM users")

# Update each user's password
for user in users:
    user_id = user['id']
    plaintext_password = user['password']
    
    # Hash the password
    hashed = hash_password_md5(plaintext_password)
    
    # Update in database
    db.execute_query(
        "UPDATE users SET password = %s WHERE id = %s",
        (hashed, user_id)
    )
    print(f"Updated user {user_id}")

print("Migration complete!")
```

---

## 💡 Tips

1. **Testing**: Gunakan endpoint `/api/hash-password` untuk generate hash
2. **Debugging**: Hash yang sama akan selalu menghasilkan output yang sama
3. **Konsistensi**: Pastikan encoding UTF-8 untuk password
4. **Database**: Kolom password harus VARCHAR(32) atau lebih

---

## 📚 Referensi

- [MD5 Wikipedia](https://en.wikipedia.org/wiki/MD5)
- [Python hashlib](https://docs.python.org/3/library/hashlib.html)
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

## 🎯 Kesimpulan

MD5 hashing sudah diimplementasikan dengan fitur:
- ✅ Hash password otomatis saat register
- ✅ Verify password saat login
- ✅ Change password dengan verifikasi password lama
- ✅ Validasi email dan password strength
- ✅ RESTful API endpoints
- ✅ Error handling yang baik

**Untuk pembelajaran**: MD5 sudah cukup  
**Untuk production**: Pertimbangkan bcrypt atau Argon2
