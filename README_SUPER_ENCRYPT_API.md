# Super Encrypt API Documentation

## Overview
API untuk encrypt dan decrypt text menggunakan **Triple Layer Encryption**:
1. **Caesar Cipher** - Shift-based substitution
2. **Vigenere Cipher** - Keyword-based polyalphabetic substitution  
3. **DES Encryption** - Data Encryption Standard

**Karakteristik:**
- ✅ **Triple Layer Security** - 3 algoritma berbeda untuk keamanan maksimal
- ✅ **Stateless API** - Text tidak disimpan di database
- ✅ **Custom Keys** - User bebas pilih semua keys (caesar shift, vigenere keyword, DES key)
- ✅ **Privacy-focused** - Server hanya memproses, tidak menyimpan
- ✅ **Base64 output** - Hasil encryption dalam format base64

---

## How It Works

### Encryption Flow
```
Plaintext
   ↓
[1] Caesar Cipher (shift key)
   ↓
[2] Vigenere Cipher (keyword)
   ↓
[3] DES Encryption (8-byte key)
   ↓
Ciphertext (base64) + IV (base64)
```

### Decryption Flow (Reverse)
```
Ciphertext + IV
   ↓
[3] DES Decryption
   ↓
[2] Vigenere Decryption
   ↓
[1] Caesar Decryption
   ↓
Plaintext
```

---

## Endpoints

### 1. Super Encrypt
Encrypt text dengan triple layer encryption.

**Endpoint:** `POST /api/super-encrypt`

**Request Body:**
```json
{
  "text": "Hello World",
  "caesar_shift": 3,
  "vigenere_key": "SECRET",
  "des_key": "mykey123"
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | ✅ Yes | - | Text yang akan dienkripsi |
| `caesar_shift` | integer | ❌ No | `3` | Shift untuk Caesar (1-25) |
| `vigenere_key` | string | ❌ No | `"KEY"` | Keyword untuk Vigenere |
| `des_key` | string | ❌ No | `"secret12"` | Key untuk DES (8 chars) |

**Response Success (200):**
```json
{
  "success": true,
  "message": "Text berhasil dienkripsi dengan Super Encrypt",
  "data": {
    "ciphertext": "HCpB6JHKG1JjxqxATEyBqQ==",
    "iv": "TxLNYiK77XA=",
    "original_length": 11,
    "algorithm": "Caesar → Vigenere → DES",
    "note": "Simpan ciphertext, iv, dan semua keys untuk dekripsi"
  }
}
```

**Response Error (400/500):**
```json
{
  "success": false,
  "error_type": "ENCRYPTION_ERROR",
  "message": "Error saat super encrypt: <details>"
}
```

---

### 2. Super Decrypt
Decrypt text yang sudah dienkripsi dengan Super Encrypt.

**Endpoint:** `POST /api/super-decrypt`

**Request Body:**
```json
{
  "ciphertext": "HCpB6JHKG1JjxqxATEyBqQ==",
  "iv": "TxLNYiK77XA=",
  "caesar_shift": 3,
  "vigenere_key": "SECRET",
  "des_key": "mykey123"
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ciphertext` | string | ✅ Yes | Ciphertext base64 dari hasil encrypt |
| `iv` | string | ✅ Yes | IV base64 dari hasil encrypt |
| `caesar_shift` | integer | ✅ Yes | Shift Caesar (harus sama dengan encrypt) |
| `vigenere_key` | string | ✅ Yes | Keyword Vigenere (harus sama) |
| `des_key` | string | ✅ Yes | Key DES (harus sama) |

**Response Success (200):**
```json
{
  "success": true,
  "message": "Text berhasil didekripsi",
  "data": {
    "plaintext": "Hello World",
    "length": 11,
    "algorithm": "DES → Vigenere → Caesar"
  }
}
```

**Response Error - Wrong Key (400):**
```json
{
  "success": false,
  "error_type": "WRONG_KEY",
  "message": "Key atau password salah",
  "details": "<error_details>"
}
```

**Response Error - Decryption Failed (500):**
```json
{
  "success": false,
  "error_type": "DECRYPTION_ERROR",
  "message": "Error saat super decrypt: <details>"
}
```

---

## Usage Examples

### A. Using Postman

#### 1. **Encrypt Text**

**Step 1:** Method `POST`, URL:
```
http://192.168.18.239:5000/api/super-encrypt
```

**Step 2:** Headers:
```
Content-Type: application/json
```

**Step 3:** Body (raw JSON):
```json
{
  "text": "This is a secret message!",
  "caesar_shift": 7,
  "vigenere_key": "CRYPTO",
  "des_key": "pass1234"
}
```

**Step 4:** Click **Send**

**Step 5:** Save response untuk decrypt nanti:
```json
{
  "success": true,
  "data": {
    "ciphertext": "ED1h7RiG3MdUqqQzaomq5w==",
    "iv": "NEPQTzthsDQ=",
    "original_length": 25,
    "algorithm": "Caesar → Vigenere → DES"
  }
}
```

---

#### 2. **Decrypt Text**

**Step 1:** Method `POST`, URL:
```
http://192.168.18.239:5000/api/super-decrypt
```

**Step 2:** Body (copy ciphertext dan iv dari encrypt response):
```json
{
  "ciphertext": "ED1h7RiG3MdUqqQzaomq5w==",
  "iv": "NEPQTzthsDQ=",
  "caesar_shift": 7,
  "vigenere_key": "CRYPTO",
  "des_key": "pass1234"
}
```

**Step 3:** Click **Send**

**Step 4:** Get plaintext back:
```json
{
  "success": true,
  "data": {
    "plaintext": "This is a secret message!",
    "length": 25
  }
}
```

---

### B. Using Python

#### 1. **Encrypt**

```python
import requests
import json

# API endpoint
url = 'http://192.168.18.239:5000/api/super-encrypt'

# Data to encrypt
data = {
    'text': 'Secret Message 123',
    'caesar_shift': 5,
    'vigenere_key': 'MYKEY',
    'des_key': 'secure12'
}

# Send request
response = requests.post(url, json=data)
result = response.json()

if result['success']:
    print('✅ Encryption Success!')
    print(f"Ciphertext: {result['data']['ciphertext']}")
    print(f"IV: {result['data']['iv']}")
    
    # Save untuk decrypt
    encrypted_data = {
        'ciphertext': result['data']['ciphertext'],
        'iv': result['data']['iv'],
        'caesar_shift': 5,
        'vigenere_key': 'MYKEY',
        'des_key': 'secure12'
    }
    
    # Save to file
    with open('encrypted_data.json', 'w') as f:
        json.dump(encrypted_data, f)
else:
    print(f"❌ Error: {result['message']}")
```

#### 2. **Decrypt**

```python
import requests
import json

# Load encrypted data
with open('encrypted_data.json', 'r') as f:
    encrypted_data = json.load(f)

# API endpoint
url = 'http://192.168.18.239:5000/api/super-decrypt'

# Send decrypt request
response = requests.post(url, json=encrypted_data)
result = response.json()

if result['success']:
    print('✅ Decryption Success!')
    print(f"Plaintext: {result['data']['plaintext']}")
else:
    print(f"❌ Error: {result['message']}")
    if result.get('error_type') == 'WRONG_KEY':
        print('⚠️ One or more keys are incorrect!')
```

#### 3. **Complete Example**

```python
import requests

class SuperEncryptAPI:
    def __init__(self, base_url='http://192.168.18.239:5000'):
        self.base_url = base_url
    
    def encrypt(self, text, caesar_shift=3, vigenere_key='KEY', des_key='secret12'):
        """Encrypt text dengan Super Encrypt"""
        url = f'{self.base_url}/api/super-encrypt'
        
        data = {
            'text': text,
            'caesar_shift': caesar_shift,
            'vigenere_key': vigenere_key,
            'des_key': des_key
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result['success']:
            return {
                'ciphertext': result['data']['ciphertext'],
                'iv': result['data']['iv'],
                'caesar_shift': caesar_shift,
                'vigenere_key': vigenere_key,
                'des_key': des_key
            }
        else:
            raise Exception(result['message'])
    
    def decrypt(self, encrypted_data):
        """Decrypt text dengan Super Encrypt"""
        url = f'{self.base_url}/api/super-decrypt'
        
        response = requests.post(url, json=encrypted_data)
        result = response.json()
        
        if result['success']:
            return result['data']['plaintext']
        else:
            raise Exception(result['message'])

# Usage
api = SuperEncryptAPI()

# Encrypt
plaintext = "Hello World from Python!"
encrypted = api.encrypt(
    text=plaintext,
    caesar_shift=7,
    vigenere_key='PYTHON',
    des_key='mykey123'
)

print(f"Encrypted: {encrypted['ciphertext']}")

# Decrypt
decrypted = api.decrypt(encrypted)
print(f"Decrypted: {decrypted}")
print(f"Match: {plaintext == decrypted}")
```

---

### C. Using Flutter/Dart

#### 1. **Service Class**

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class SuperEncryptService {
  final String baseUrl = 'http://192.168.18.239:5000';
  
  Future<Map<String, dynamic>> encrypt({
    required String text,
    int caesarShift = 3,
    String vigenereKey = 'KEY',
    String desKey = 'secret12',
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/super-encrypt'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text': text,
        'caesar_shift': caesarShift,
        'vigenere_key': vigenereKey,
        'des_key': desKey,
      }),
    );
    
    final result = jsonDecode(response.body);
    
    if (result['success']) {
      return {
        'ciphertext': result['data']['ciphertext'],
        'iv': result['data']['iv'],
        'caesar_shift': caesarShift,
        'vigenere_key': vigenereKey,
        'des_key': desKey,
      };
    } else {
      throw Exception(result['message']);
    }
  }
  
  Future<String> decrypt(Map<String, dynamic> encryptedData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/super-decrypt'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(encryptedData),
    );
    
    final result = jsonDecode(response.body);
    
    if (result['success']) {
      return result['data']['plaintext'];
    } else {
      if (result['error_type'] == 'WRONG_KEY') {
        throw Exception('Wrong encryption keys!');
      }
      throw Exception(result['message']);
    }
  }
}
```

#### 2. **Usage Example**

```dart
void main() async {
  final api = SuperEncryptService();
  
  // Encrypt
  String plaintext = 'Secret Flutter Message';
  
  try {
    final encrypted = await api.encrypt(
      text: plaintext,
      caesarShift: 5,
      vigenereKey: 'FLUTTER',
      desKey: 'dart1234',
    );
    
    print('✅ Encrypted successfully!');
    print('Ciphertext: ${encrypted['ciphertext']}');
    print('IV: ${encrypted['iv']}');
    
    // Decrypt
    final decrypted = await api.decrypt(encrypted);
    print('✅ Decrypted: $decrypted');
    print('Match: ${plaintext == decrypted}');
    
  } catch (e) {
    print('❌ Error: $e');
  }
}
```

#### 3. **Complete Flutter UI Example**

```dart
import 'package:flutter/material.dart';

class SuperEncryptScreen extends StatefulWidget {
  @override
  _SuperEncryptScreenState createState() => _SuperEncryptScreenState();
}

class _SuperEncryptScreenState extends State<SuperEncryptScreen> {
  final _textController = TextEditingController();
  final _caesarController = TextEditingController(text: '3');
  final _vigenereController = TextEditingController(text: 'KEY');
  final _desController = TextEditingController(text: 'secret12');
  
  final _service = SuperEncryptService();
  Map<String, dynamic>? _encryptedData;
  String _result = '';
  
  Future<void> _encrypt() async {
    try {
      _encryptedData = await _service.encrypt(
        text: _textController.text,
        caesarShift: int.parse(_caesarController.text),
        vigenereKey: _vigenereController.text,
        desKey: _desController.text,
      );
      
      setState(() {
        _result = '✅ Encrypted!\nCiphertext: ${_encryptedData!['ciphertext']}';
      });
    } catch (e) {
      setState(() {
        _result = '❌ Error: $e';
      });
    }
  }
  
  Future<void> _decrypt() async {
    if (_encryptedData == null) {
      setState(() {
        _result = '❌ No encrypted data!';
      });
      return;
    }
    
    try {
      final plaintext = await _service.decrypt(_encryptedData!);
      setState(() {
        _result = '✅ Decrypted: $plaintext';
      });
    } catch (e) {
      setState(() {
        _result = '❌ Error: $e';
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Super Encrypt')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _textController,
              decoration: InputDecoration(labelText: 'Text'),
            ),
            SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _caesarController,
                    decoration: InputDecoration(labelText: 'Caesar Shift'),
                    keyboardType: TextInputType.number,
                  ),
                ),
                SizedBox(width: 8),
                Expanded(
                  child: TextField(
                    controller: _vigenereController,
                    decoration: InputDecoration(labelText: 'Vigenere Key'),
                  ),
                ),
              ],
            ),
            SizedBox(height: 8),
            TextField(
              controller: _desController,
              decoration: InputDecoration(labelText: 'DES Key (8 chars)'),
            ),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: _encrypt,
                    child: Text('Encrypt'),
                  ),
                ),
                SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _decrypt,
                    child: Text('Decrypt'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text(_result),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## Algorithm Details

### 1. Caesar Cipher
- **Type:** Substitution cipher
- **Method:** Shift each letter by N positions
- **Key:** Integer (1-25)
- **Example:** 
  - Shift = 3
  - "HELLO" → "KHOOR"
  - A→D, B→E, C→F, ..., X→A, Y→B, Z→C

### 2. Vigenere Cipher
- **Type:** Polyalphabetic substitution
- **Method:** Use repeating keyword for varying shifts
- **Key:** String (alphabetic)
- **Example:**
  - Keyword = "KEY"
  - "HELLO" → "RIJVS"
  - H+K=R, E+E=I, L+Y=J, L+K=V, O+E=S

### 3. DES (Data Encryption Standard)
- **Type:** Symmetric block cipher
- **Block Size:** 64 bits (8 bytes)
- **Key Size:** 56 bits effective (8 bytes with parity)
- **Mode:** CBC (Cipher Block Chaining)
- **IV:** Random 8-byte initialization vector

---

## Key Requirements

### Caesar Shift
- **Type:** Integer
- **Range:** 1-25 (will normalize if >25)
- **Default:** 3
- **Example:** `5`, `13` (ROT13), `7`

### Vigenere Key
- **Type:** String (alphabetic)
- **Length:** 1+ characters
- **Case:** Insensitive (converted to uppercase)
- **Default:** `"KEY"`
- **Example:** `"SECRET"`, `"CRYPTO"`, `"PASSWORD"`

### DES Key
- **Type:** String
- **Length:** Exactly 8 characters
- **Auto-fix:** Padded with spaces if <8, truncated if >8
- **Default:** `"secret12"`
- **Example:** `"mykey123"`, `"pass1234"`, `"secure99"`

---

## Security Notes

⚠️ **Important:**
- **Triple Layer** - Lebih aman dari single encryption
- **All keys required** - Decrypt butuh semua keys yang sama
- **No key storage** - Server tidak menyimpan keys
- **Stateless** - Tidak ada database storage
- **IV Random** - Setiap encryption menghasilkan IV berbeda

💡 **Best Practices:**
- Gunakan caesar shift > 5 untuk keamanan lebih
- Vigenere key minimal 6 karakter
- DES key jangan mudah ditebak
- Jangan share keys di tempat tidak aman
- Backup ciphertext, IV, dan semua keys
- Simpan keys terpisah dari ciphertext

⚡ **Performance:**
- Fast encryption/decryption
- Minimal memory usage
- No file I/O overhead
- Stateless = no database queries

---

## Error Handling

| Error Type | HTTP Code | Cause | Solution |
|------------|-----------|-------|----------|
| `ENCRYPTION_ERROR` | 500 | Gagal encrypt | Check input text |
| `DECRYPTION_ERROR` | 500 | Gagal decrypt | Check ciphertext format |
| `WRONG_KEY` | 400 | Keys salah | Gunakan keys yang benar |
| Missing `text` | 400 | Field required | Include text in encrypt request |
| Missing keys | 400 | Field required | Include all keys in decrypt request |

---

## Testing

### Manual Test with cURL

#### Encrypt:
```bash
curl -X POST http://192.168.18.239:5000/api/super-encrypt \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test Message",
    "caesar_shift": 5,
    "vigenere_key": "SECRET",
    "des_key": "test1234"
  }'
```

#### Decrypt:
```bash
curl -X POST http://192.168.18.239:5000/api/super-decrypt \
  -H "Content-Type: application/json" \
  -d '{
    "ciphertext": "YOUR_CIPHERTEXT_HERE",
    "iv": "YOUR_IV_HERE",
    "caesar_shift": 5,
    "vigenere_key": "SECRET",
    "des_key": "test1234"
  }'
```

### Testing Checklist
- [ ] Encrypt dengan default keys
- [ ] Encrypt dengan custom keys
- [ ] Decrypt dengan correct keys
- [ ] Decrypt dengan wrong caesar shift (should fail)
- [ ] Decrypt dengan wrong vigenere key (should fail)
- [ ] Decrypt dengan wrong DES key (should fail)
- [ ] Encrypt long text (>100 chars)
- [ ] Encrypt dengan special characters
- [ ] Encrypt dengan numbers
- [ ] Verify plaintext == decrypted

---

## API URLs

### Local Development
- Localhost: `http://127.0.0.1:5000`

### Network Access
- Same network: `http://192.168.18.239:5000`
- Android Emulator: `http://10.0.2.2:5000`

### Endpoints
- Encrypt: `POST /api/super-encrypt`
- Decrypt: `POST /api/super-decrypt`
- Homepage: `GET /` (list all endpoints)

---

## Comparison with Other Encryption

| Feature | Super Encrypt | AES File Encryption | DES Message |
|---------|---------------|---------------------|-------------|
| Layers | 3 (Caesar+Vigenere+DES) | 1 (AES-256) | 1 (DES) |
| Input | Text only | Any file type | Text only |
| Output | Base64 text | Base64 file | Base64 text |
| Keys | 3 different keys | 1 password | 1 key (8 bytes) |
| Security | High (triple layer) | Very High (AES-256) | Medium (DES) |
| Speed | Fast | Medium | Very Fast |
| Use Case | Secret messages | File protection | Message storage |

---

## FAQ

**Q: Kenapa pakai 3 algoritma?**
A: Triple layer encryption memberikan keamanan lebih tinggi. Bahkan jika 1 layer berhasil dipecahkan, masih ada 2 layer lagi.

**Q: Apakah DES aman?**
A: DES sendiri sudah outdated, tetapi dalam Super Encrypt, DES adalah layer ke-3 setelah Caesar dan Vigenere, jadi tetap aman untuk use case general.

**Q: Bisa decrypt tanpa salah satu key?**
A: Tidak! Semua 3 keys harus sama persis dengan yang digunakan saat encrypt.

**Q: Apakah ciphertext selalu sama untuk text yang sama?**
A: Tidak! Karena DES menggunakan random IV, setiap encryption menghasilkan ciphertext berbeda.

**Q: Maksimal panjang text?**
A: Tidak ada limit, tetapi untuk text sangat panjang (>10KB), pertimbangkan gunakan file encryption API.

**Q: Apakah keys disimpan di server?**
A: Tidak! API ini stateless. Server hanya memproses, tidak menyimpan apapun.

---

## Changelog

### Version 1.0 (Current)
- ✅ Triple layer encryption (Caesar → Vigenere → DES)
- ✅ Custom keys untuk semua layers
- ✅ Stateless API (no database)
- ✅ Base64 output
- ✅ Random IV untuk DES
- ✅ Wrong key detection
- ✅ Complete error handling

---

**Need Help?**
- Check server logs untuk error details
- Verify semua keys match antara encrypt dan decrypt
- Test dengan simple text dulu (e.g., "Hello")
- Pastikan DES key exactly 8 characters
- Verify ciphertext dan IV tidak corrupted

**Happy Encrypting! 🔐🔐🔐**
