# File Encryption API Documentation

## Overview
API untuk encrypt dan decrypt file menggunakan algoritma **AES-256-CBC**.

**Karakteristik:**
- ✅ **Stateless API** - File tidak disimpan di server atau database
- ✅ **Privacy-focused** - Server hanya memproses, tidak menyimpan
- ✅ **Supports all file types** - PDF, images, documents, videos, etc.
- ✅ **AES-256-CBC** - Encryption dengan IV (Initialization Vector) random
- ✅ **Base64 transfer** - File dikirim dan diterima dalam format base64

---

## Endpoints

### 1. Encrypt File
Encrypt file dengan password.

**Endpoint:** `POST /api/file/encrypt`

**Request Body:**
```json
{
  "file_data": "base64_encoded_file",
  "password": "your_strong_password",
  "filename": "document.pdf"
}
```

**Response Success (200):**
```json
{
  "success": true,
  "message": "File berhasil dienkripsi",
  "data": {
    "encrypted_file": "base64_encrypted_data",
    "original_size": 12345,
    "encrypted_size": 12368,
    "algorithm": "AES-256-CBC",
    "filename": "document.pdf.enc",
    "note": "Download file dengan decode base64"
  }
}
```

**Response Error (400/500):**
```json
{
  "success": false,
  "error_type": "ENCRYPTION_ERROR",
  "message": "Error saat enkripsi: <error_details>"
}
```

---

### 2. Decrypt File
Decrypt file yang sudah dienkripsi.

**Endpoint:** `POST /api/file/decrypt`

**Request Body:**
```json
{
  "file_data": "base64_encrypted_file",
  "password": "your_strong_password",
  "filename": "document.pdf.enc"
}
```

**Response Success (200):**
```json
{
  "success": true,
  "message": "File berhasil didekripsi",
  "data": {
    "decrypted_file": "base64_original_data",
    "decrypted_size": 12345,
    "algorithm": "AES-256-CBC",
    "filename": "document.pdf",
    "note": "Download file dengan decode base64"
  }
}
```

**Response Error - Wrong Password (400):**
```json
{
  "success": false,
  "error_type": "WRONG_PASSWORD",
  "message": "Password salah atau file rusak",
  "details": "<error_details>"
}
```

**Response Error - Decryption Failed (500):**
```json
{
  "success": false,
  "error_type": "DECRYPTION_ERROR",
  "message": "Error saat dekripsi: <error_details>"
}
```

---

## How to Use

### A. Upload File untuk Encrypt

#### 1. **Using Postman**

**Step 1:** Pilih method `POST` dan URL:
```
http://192.168.18.239:5000/api/file/encrypt
```

**Step 2:** Di tab **Body**, pilih **raw** dan **JSON**

**Step 3:** Siapkan file dalam base64. Ada 2 cara:

**Cara 1 - Manual convert file to base64:**
```bash
# Di Windows PowerShell
$fileContent = [System.IO.File]::ReadAllBytes("C:\path\to\document.pdf")
$base64String = [System.Convert]::ToBase64String($fileContent)
$base64String | Set-Clipboard
```

**Cara 2 - Gunakan online base64 encoder:**
- Upload file ke https://base64.guru/converter/encode/file
- Copy hasil base64

**Step 4:** Paste ke request body:
```json
{
  "file_data": "JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PC9UeXBlIC9QYWdlCi9QYXJl...",
  "password": "MySecurePassword123",
  "filename": "document.pdf"
}
```

**Step 5:** Klik **Send**

**Step 6:** Copy `encrypted_file` dari response dan save ke file:
```bash
# PowerShell - Save encrypted file
$encryptedBase64 = "paste_encrypted_base64_here"
$encryptedBytes = [System.Convert]::FromBase64String($encryptedBase64)
[System.IO.File]::WriteAllBytes("C:\path\to\document.pdf.enc", $encryptedBytes)
```

---

#### 2. **Using Python**

```python
import requests
import base64

# Read file
with open('document.pdf', 'rb') as f:
    file_bytes = f.read()
    file_base64 = base64.b64encode(file_bytes).decode('utf-8')

# Encrypt request
response = requests.post('http://192.168.18.239:5000/api/file/encrypt', json={
    'file_data': file_base64,
    'password': 'MySecurePassword123',
    'filename': 'document.pdf'
})

result = response.json()
print(result['message'])

# Save encrypted file
if result['success']:
    encrypted_base64 = result['data']['encrypted_file']
    encrypted_bytes = base64.b64decode(encrypted_base64)
    
    with open('document.pdf.enc', 'wb') as f:
        f.write(encrypted_bytes)
    
    print(f"✅ File encrypted: document.pdf.enc")
    print(f"📊 Original size: {result['data']['original_size']} bytes")
    print(f"📊 Encrypted size: {result['data']['encrypted_size']} bytes")
```

---

#### 3. **Using Flutter/Dart**

```dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';

Future<File?> encryptFile(File file, String password) async {
  try {
    // Read file as bytes
    final bytes = await file.readAsBytes();
    final base64File = base64Encode(bytes);
    
    // API request
    final response = await http.post(
      Uri.parse('http://192.168.18.239:5000/api/file/encrypt'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'file_data': base64File,
        'password': password,
        'filename': file.path.split('/').last,
      }),
    );
    
    final result = jsonDecode(response.body);
    
    if (result['success']) {
      // Decode encrypted file
      final encryptedBase64 = result['data']['encrypted_file'];
      final encryptedBytes = base64Decode(encryptedBase64);
      
      // Save to file
      final directory = await getApplicationDocumentsDirectory();
      final encryptedFile = File('${directory.path}/${result['data']['filename']}');
      await encryptedFile.writeAsBytes(encryptedBytes);
      
      print('✅ File encrypted: ${encryptedFile.path}');
      return encryptedFile;
    } else {
      print('❌ Encryption failed: ${result['message']}');
      return null;
    }
  } catch (e) {
    print('❌ Error: $e');
    return null;
  }
}

// Usage
void main() async {
  File myFile = File('/path/to/document.pdf');
  File? encrypted = await encryptFile(myFile, 'MySecurePassword123');
  
  if (encrypted != null) {
    print('Encrypted file saved at: ${encrypted.path}');
  }
}
```

---

### B. Upload File untuk Decrypt

#### 1. **Using Postman**

**Step 1:** Method `POST`, URL:
```
http://192.168.18.239:5000/api/file/decrypt
```

**Step 2:** Convert encrypted file to base64:
```bash
# PowerShell
$fileContent = [System.IO.File]::ReadAllBytes("C:\path\to\document.pdf.enc")
$base64String = [System.Convert]::ToBase64String($fileContent)
$base64String | Set-Clipboard
```

**Step 3:** Request body:
```json
{
  "file_data": "paste_encrypted_base64_here",
  "password": "MySecurePassword123",
  "filename": "document.pdf.enc"
}
```

**Step 4:** Send request

**Step 5:** Save decrypted file:
```bash
# PowerShell
$decryptedBase64 = "paste_decrypted_base64_here"
$decryptedBytes = [System.Convert]::FromBase64String($decryptedBase64)
[System.IO.File]::WriteAllBytes("C:\path\to\document_decrypted.pdf", $decryptedBytes)
```

---

#### 2. **Using Python**

```python
import requests
import base64

# Read encrypted file
with open('document.pdf.enc', 'rb') as f:
    encrypted_bytes = f.read()
    encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')

# Decrypt request
response = requests.post('http://192.168.18.239:5000/api/file/decrypt', json={
    'file_data': encrypted_base64,
    'password': 'MySecurePassword123',
    'filename': 'document.pdf.enc'
})

result = response.json()

if result['success']:
    # Save decrypted file
    decrypted_base64 = result['data']['decrypted_file']
    decrypted_bytes = base64.b64decode(decrypted_base64)
    
    with open('document_decrypted.pdf', 'wb') as f:
        f.write(decrypted_bytes)
    
    print(f"✅ File decrypted: document_decrypted.pdf")
    print(f"📊 Size: {result['data']['decrypted_size']} bytes")
else:
    print(f"❌ Decryption failed: {result['message']}")
    if result.get('error_type') == 'WRONG_PASSWORD':
        print("⚠️ Password salah!")
```

---

#### 3. **Using Flutter/Dart**

```dart
Future<File?> decryptFile(File encryptedFile, String password) async {
  try {
    // Read encrypted file
    final bytes = await encryptedFile.readAsBytes();
    final base64File = base64Encode(bytes);
    
    // API request
    final response = await http.post(
      Uri.parse('http://192.168.18.239:5000/api/file/decrypt'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'file_data': base64File,
        'password': password,
        'filename': encryptedFile.path.split('/').last,
      }),
    );
    
    final result = jsonDecode(response.body);
    
    if (result['success']) {
      // Decode decrypted file
      final decryptedBase64 = result['data']['decrypted_file'];
      final decryptedBytes = base64Decode(decryptedBase64);
      
      // Save to file
      final directory = await getApplicationDocumentsDirectory();
      final decryptedFile = File('${directory.path}/${result['data']['filename']}');
      await decryptedFile.writeAsBytes(decryptedBytes);
      
      print('✅ File decrypted: ${decryptedFile.path}');
      return decryptedFile;
    } else {
      if (result['error_type'] == 'WRONG_PASSWORD') {
        print('❌ Password salah!');
      } else {
        print('❌ Decryption failed: ${result['message']}');
      }
      return null;
    }
  } catch (e) {
    print('❌ Error: $e');
    return null;
  }
}
```

---

## Complete Flutter Example (File Picker + Encrypt/Decrypt)

```dart
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';

class FileEncryptionScreen extends StatefulWidget {
  @override
  _FileEncryptionScreenState createState() => _FileEncryptionScreenState();
}

class _FileEncryptionScreenState extends State<FileEncryptionScreen> {
  final _passwordController = TextEditingController();
  String _status = 'Select a file to encrypt or decrypt';
  File? _selectedFile;
  bool _isLoading = false;

  // Pick file
  Future<void> _pickFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles();
    
    if (result != null) {
      setState(() {
        _selectedFile = File(result.files.single.path!);
        _status = 'Selected: ${result.files.single.name}';
      });
    }
  }

  // Encrypt file
  Future<void> _encryptFile() async {
    if (_selectedFile == null) {
      _showError('Please select a file first');
      return;
    }
    
    if (_passwordController.text.isEmpty) {
      _showError('Please enter a password');
      return;
    }

    setState(() {
      _isLoading = true;
      _status = 'Encrypting...';
    });

    try {
      // Read file
      final bytes = await _selectedFile!.readAsBytes();
      final base64File = base64Encode(bytes);
      
      // API call
      final response = await http.post(
        Uri.parse('http://192.168.18.239:5000/api/file/encrypt'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'file_data': base64File,
          'password': _passwordController.text,
          'filename': _selectedFile!.path.split('/').last,
        }),
      );
      
      final result = jsonDecode(response.body);
      
      if (result['success']) {
        // Save encrypted file
        final encryptedBase64 = result['data']['encrypted_file'];
        final encryptedBytes = base64Decode(encryptedBase64);
        
        final directory = await getApplicationDocumentsDirectory();
        final encryptedFile = File('${directory.path}/${result['data']['filename']}');
        await encryptedFile.writeAsBytes(encryptedBytes);
        
        setState(() {
          _status = '✅ Encrypted successfully!\n📁 ${encryptedFile.path}';
          _selectedFile = encryptedFile;
        });
        
        _showSuccess('File encrypted successfully!');
      } else {
        _showError(result['message']);
      }
    } catch (e) {
      _showError('Error: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  // Decrypt file
  Future<void> _decryptFile() async {
    if (_selectedFile == null) {
      _showError('Please select an encrypted file');
      return;
    }
    
    if (_passwordController.text.isEmpty) {
      _showError('Please enter password');
      return;
    }

    setState(() {
      _isLoading = true;
      _status = 'Decrypting...';
    });

    try {
      // Read encrypted file
      final bytes = await _selectedFile!.readAsBytes();
      final base64File = base64Encode(bytes);
      
      // API call
      final response = await http.post(
        Uri.parse('http://192.168.18.239:5000/api/file/decrypt'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'file_data': base64File,
          'password': _passwordController.text,
          'filename': _selectedFile!.path.split('/').last,
        }),
      );
      
      final result = jsonDecode(response.body);
      
      if (result['success']) {
        // Save decrypted file
        final decryptedBase64 = result['data']['decrypted_file'];
        final decryptedBytes = base64Decode(decryptedBase64);
        
        final directory = await getApplicationDocumentsDirectory();
        final decryptedFile = File('${directory.path}/${result['data']['filename']}');
        await decryptedFile.writeAsBytes(decryptedBytes);
        
        setState(() {
          _status = '✅ Decrypted successfully!\n📁 ${decryptedFile.path}';
          _selectedFile = decryptedFile;
        });
        
        _showSuccess('File decrypted successfully!');
      } else {
        if (result['error_type'] == 'WRONG_PASSWORD') {
          _showError('❌ Wrong password!');
        } else {
          _showError(result['message']);
        }
      }
    } catch (e) {
      _showError('Error: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red)
    );
    setState(() => _status = message);
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.green)
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('File Encryption')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // File picker button
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _pickFile,
              icon: Icon(Icons.folder_open),
              label: Text('Select File'),
            ),
            
            SizedBox(height: 16),
            
            // Password input
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(
                labelText: 'Password',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.lock),
              ),
              obscureText: true,
            ),
            
            SizedBox(height: 16),
            
            // Encrypt button
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _encryptFile,
              icon: Icon(Icons.lock),
              label: Text('Encrypt File'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.blue),
            ),
            
            SizedBox(height: 8),
            
            // Decrypt button
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _decryptFile,
              icon: Icon(Icons.lock_open),
              label: Text('Decrypt File'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            ),
            
            SizedBox(height: 24),
            
            // Status
            if (_isLoading)
              Center(child: CircularProgressIndicator())
            else
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    _status,
                    style: TextStyle(fontSize: 14),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
```

**Add dependencies to `pubspec.yaml`:**
```yaml
dependencies:
  file_picker: ^8.0.0+1
  http: ^1.2.0
  path_provider: ^2.1.1
```

---

## Technical Details

### Encryption Process
1. **Password → Key**: Password diubah jadi 32-byte key (AES-256)
   - Jika password < 32 chars: dipadding dengan spasi
   - Jika password > 32 chars: dipotong jadi 32 chars

2. **IV Generation**: Random 16-byte IV untuk setiap encryption

3. **Encryption**: AES-256-CBC dengan padding PKCS7

4. **Output Format**: `IV (16 bytes) + Ciphertext`

5. **Base64 Encoding**: Binary data di-encode ke base64 untuk transfer

### Decryption Process
1. **Extract IV**: Ambil 16 bytes pertama dari encrypted data

2. **Extract Ciphertext**: Sisa data setelah IV

3. **Decrypt**: AES-256-CBC decrypt dengan IV dan password

4. **Unpad**: Remove PKCS7 padding

5. **Return**: Original file data dalam base64

---

## Security Notes

⚠️ **Important:**
- **Password tidak di-hash** - Password langsung digunakan sebagai key (setelah padding/truncate)
- **Stateless** - Server tidak menyimpan file atau password
- **IV Random** - Setiap encryption menghasilkan ciphertext berbeda
- **No Key Derivation** - Tidak menggunakan PBKDF2 atau similar (simple implementation)

💡 **Recommendations:**
- Gunakan password minimal 12 karakter
- Kombinasi huruf besar, kecil, angka, dan simbol
- Jangan lupa password - tidak bisa recover file jika lupa!
- Backup encrypted file di tempat aman
- Jangan kirim password bersamaan dengan encrypted file

---

## Supported File Types

✅ **All file types supported:**
- Documents: PDF, DOCX, TXT, XLSX, PPTX
- Images: JPG, PNG, GIF, BMP, WEBP, SVG
- Videos: MP4, AVI, MKV, MOV
- Audio: MP3, WAV, FLAC, AAC
- Archives: ZIP, RAR, 7Z, TAR
- Executables: EXE, APK, DLL
- Dan semua format file lainnya!

---

## File Size Limits

⚠️ **Base64 Overhead:**
- Base64 encoding menambah ~33% size
- Contoh: File 1MB → Base64 ~1.33MB → Encrypted ~1.35MB

💡 **Recommendations:**
- Untuk file besar (>10MB), pertimbangkan chunking
- Monitor memory usage untuk file >50MB
- Consider compression sebelum encryption untuk file besar

---

## Error Handling

| Error Type | HTTP Code | Cause | Solution |
|------------|-----------|-------|----------|
| `ENCRYPTION_ERROR` | 500 | Gagal encrypt file | Check file integrity |
| `DECRYPTION_ERROR` | 500 | Gagal decrypt file | Check file format |
| `WRONG_PASSWORD` | 400 | Password salah | Gunakan password yang benar |
| Missing `file_data` | 400 | Field required | Include file_data in request |
| Missing `password` | 400 | Field required | Include password in request |
| Invalid base64 | 400 | Base64 tidak valid | Check encoding |

---

## Testing Checklist

- [ ] Encrypt text file (.txt)
- [ ] Decrypt with correct password
- [ ] Decrypt with wrong password (should fail)
- [ ] Encrypt PDF file
- [ ] Encrypt image (JPG/PNG)
- [ ] Encrypt large file (>5MB)
- [ ] Verify decrypted file matches original
- [ ] Test with special characters in filename
- [ ] Test with very long password (>32 chars)
- [ ] Test with empty password (should work but insecure)

---

## API URLs

### Local Development
- Localhost: `http://127.0.0.1:5000`

### Network Access
- Same network: `http://192.168.18.239:5000`
- Android Emulator: `http://10.0.2.2:5000`

### Endpoints
- Encrypt: `POST /api/file/encrypt`
- Decrypt: `POST /api/file/decrypt`
- Homepage: `GET /` (list all endpoints)

---

## Changelog

### Version 1.0 (Current)
- ✅ File encryption dengan AES-256-CBC
- ✅ File decryption dengan password
- ✅ Stateless API (no database, no file storage)
- ✅ Base64 file transfer
- ✅ Support all file types
- ✅ Automatic .enc extension handling
- ✅ Wrong password detection

---

**Need Help?** 
- Check server logs untuk error details
- Verify network connectivity dengan `GET /` endpoint
- Test dengan small file dulu sebelum large files
- Pastikan base64 encoding benar (no whitespace, no line breaks)

**Happy Encrypting! 🔐**
