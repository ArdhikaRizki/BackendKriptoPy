# 🎯 Steganography Stateless API

## Overview

**NO DATABASE! NO FILE STORAGE! PURE PROCESSING ONLY!**

API ini hanya melakukan **processing** steganografi tanpa menyimpan apa-apa ke server:
- ✅ Encode: Upload gambar + pesan → return gambar hasil (base64)
- ✅ Decode: Upload gambar stego → return pesan rahasia
- ❌ Tidak save ke database
- ❌ Tidak save ke file server
- ❌ Tidak perlu login/user_id

**Use Case:**
User bisa encode/decode gambar secara **instant**, download hasilnya sendiri, dan share ke teman. Server hanya sebagai **processor**, bukan **storage**.

---

## 📋 Endpoints

### 1️⃣ Encode Message to Image

**Endpoint:** `POST /api/stego/encode`

**Deskripsi:** Upload gambar original + pesan rahasia → return gambar yang sudah di-encode (base64)

#### Request:
```json
POST /api/stego/encode
Content-Type: application/json

{
  "image_data": "iVBORw0KGgoAAAANSUhEUgAA...",
  "secret_message": "Ini adalah pesan rahasia yang akan disembunyikan!"
}
```

**Parameters:**
- `image_data` (required): Base64 encoded original image (JPG, PNG, etc)
- `secret_message` (required): Pesan rahasia yang akan disembunyikan

#### Response Success (200):
```json
{
  "success": true,
  "message": "Pesan berhasil disembunyikan dalam gambar",
  "data": {
    "encoded_image": "iVBORw0KGgoAAAANSUhEUgAA...",
    "image_info": {
      "width": 1920,
      "height": 1080,
      "total_pixels": 2073600,
      "max_capacity": 777591
    },
    "message_length": 52,
    "capacity_used_percent": 0.007,
    "format": "PNG",
    "note": "Download gambar dengan decode base64 ke file PNG"
  }
}
```

**Field Explanation:**
- `encoded_image`: Base64 gambar hasil steganografi (dalam format PNG)
- `image_info`: Informasi dimensi dan kapasitas gambar
- `message_length`: Panjang pesan yang disembunyikan
- `capacity_used_percent`: Persentase kapasitas yang dipakai (0.007% = sangat kecil!)
- `format`: Selalu PNG (lossless format untuk steganografi)

#### Response Error (400):
```json
{
  "success": false,
  "message": "Pesan terlalu panjang! Maksimal 777591 karakter, pesan kamu 1000000 karakter",
  "image_info": {
    "width": 1920,
    "height": 1080,
    "max_capacity": 777591
  }
}
```

---

### 2️⃣ Decode Message from Image

**Endpoint:** `POST /api/stego/decode`

**Deskripsi:** Upload gambar steganografi → extract pesan rahasia

#### Request:
```json
POST /api/stego/decode
Content-Type: application/json

{
  "image_data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Parameters:**
- `image_data` (required): Base64 encoded steganography image (harus PNG!)

#### Response Success (200):
```json
{
  "success": true,
  "message": "Pesan berhasil diekstrak",
  "data": {
    "secret_message": "Ini adalah pesan rahasia yang akan disembunyikan!",
    "message_length": 52,
    "image_info": {
      "width": 1920,
      "height": 1080,
      "total_pixels": 2073600,
      "max_capacity": 777591
    }
  }
}
```

#### Response Error (500):
```json
{
  "success": false,
  "message": "Error decoding message: ..."
}
```

---

## 🧪 Testing dengan Postman

### Scenario: Encode → Download → Decode

#### Step 1: Encode Message
```
POST http://localhost:5000/api/stego/encode

Body (raw JSON):
{
  "image_data": "<base64 gambar original>",
  "secret_message": "Hello World Secret!"
}

Response:
{
  "success": true,
  "data": {
    "encoded_image": "iVBORw0KGgo..."  // ← Copy ini!
  }
}
```

#### Step 2: Save Encoded Image
Copy `encoded_image` dari response → paste ke file → save as PNG

**Cara convert base64 to PNG:**
- Online tool: https://base64.guru/converter/decode/image
- Python: 
  ```python
  import base64
  with open('result.png', 'wb') as f:
      f.write(base64.b64decode(encoded_image))
  ```

#### Step 3: Decode Message
```
POST http://localhost:5000/api/stego/decode

Body (raw JSON):
{
  "image_data": "<base64 gambar yang sudah di-encode>"
}

Response:
{
  "success": true,
  "data": {
    "secret_message": "Hello World Secret!"  // ← Pesan muncul!
  }
}
```

---

## 💻 Flutter Implementation

### Dependencies (pubspec.yaml):
```yaml
dependencies:
  image_picker: ^1.0.0
  image_gallery_saver: ^2.0.3  # For saving to Gallery
  http: ^1.1.0
  path_provider: ^2.1.0
```

### Complete Example:

```dart
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:image_gallery_saver/image_gallery_saver.dart';

class StatelessStegoPage extends StatefulWidget {
  @override
  State<StatelessStegoPage> createState() => _StatelessStegoPageState();
}

class _StatelessStegoPageState extends State<StatelessStegoPage> {
  final String baseUrl = 'http://10.0.2.2:5000';
  final ImagePicker _picker = ImagePicker();
  
  File? selectedImage;
  String secretMessage = '';
  bool isLoading = false;

  // ========== ENCODE ==========
  Future<void> encodeMessage() async {
    if (selectedImage == null || secretMessage.isEmpty) {
      _showError('Pilih gambar dan isi pesan terlebih dahulu');
      return;
    }

    setState(() => isLoading = true);

    try {
      // 1. Convert image to base64
      final bytes = await selectedImage!.readAsBytes();
      final base64Image = base64Encode(bytes);

      print('📤 Encoding message into image...');

      // 2. Send to API
      final response = await http.post(
        Uri.parse('$baseUrl/api/stego/encode'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'image_data': base64Image,
          'secret_message': secretMessage,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final encodedImageBase64 = data['data']['encoded_image'];

        // 3. Save encoded image to device
        await _saveEncodedImage(encodedImageBase64);

        _showSuccess('Gambar berhasil di-encode dan disimpan!');
      } else {
        final error = jsonDecode(response.body);
        _showError(error['message']);
      }
    } catch (e) {
      _showError('Error: $e');
    } finally {
      setState(() => isLoading = false);
    }
  }

  // Save base64 image to Gallery
  Future<void> _saveEncodedImage(String base64Image) async {
    try {
      // Decode base64 to bytes
      final bytes = base64Decode(base64Image);

      // Save to Gallery (visible to user!)
      final result = await ImageGallerySaver.saveImage(
        Uint8List.fromList(bytes),
        quality: 100,
        name: "stego_${DateTime.now().millisecondsSinceEpoch}",
      );

      if (result['isSuccess']) {
        print('✅ Saved to Gallery: ${result['filePath']}');
        // Android: /storage/emulated/0/Pictures/stego_xxx.png
        // iOS: Photo Library
        
        _showDialog('Success', 'Gambar berhasil disimpan ke Gallery!\nBisa dilihat di Photos/Gallery app.');
      } else {
        throw Exception('Failed to save image');
      }
    } catch (e) {
      print('❌ Error saving image: $e');
      _showError('Gagal menyimpan gambar: $e');
    }
  }

  // ========== DECODE ==========
  Future<void> decodeMessage() async {
    if (selectedImage == null) {
      _showError('Pilih gambar steganografi terlebih dahulu');
      return;
    }

    setState(() => isLoading = true);

    try {
      // 1. Convert image to base64
      final bytes = await selectedImage!.readAsBytes();
      final base64Image = base64Encode(bytes);

      print('🔓 Decoding message from image...');

      // 2. Send to API
      final response = await http.post(
        Uri.parse('$baseUrl/api/stego/decode'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'image_data': base64Image,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final decodedMessage = data['data']['secret_message'];

        // 3. Show message
        _showDialog('Secret Message Found!', decodedMessage);
      } else {
        final error = jsonDecode(response.body);
        _showError(error['message']);
      }
    } catch (e) {
      _showError('Error: $e');
    } finally {
      setState(() => isLoading = false);
    }
  }

  // Pick image from gallery
  Future<void> pickImage() async {
    final image = await _picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 100, // IMPORTANT: No compression!
    );

    if (image != null) {
      setState(() => selectedImage = File(image.path));
    }
  }

  void _showError(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: Colors.red),
    );
  }

  void _showSuccess(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: Colors.green),
    );
  }

  void _showDialog(String title, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: SelectableText(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Stateless Steganography'),
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Pick Image Button
            ElevatedButton.icon(
              icon: Icon(Icons.photo_library),
              label: Text('Pick Image'),
              onPressed: pickImage,
            ),

            if (selectedImage != null) ...[
              SizedBox(height: 16),
              Image.file(selectedImage!, height: 200, fit: BoxFit.contain),
            ],

            SizedBox(height: 24),

            // Secret Message Input
            TextField(
              decoration: InputDecoration(
                labelText: 'Secret Message',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
              onChanged: (value) => setState(() => secretMessage = value),
            ),

            SizedBox(height: 16),

            // Encode Button
            ElevatedButton.icon(
              icon: Icon(Icons.lock),
              label: Text('Encode & Download'),
              onPressed: isLoading ? null : encodeMessage,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                padding: EdgeInsets.symmetric(vertical: 16),
              ),
            ),

            SizedBox(height: 8),

            // Decode Button
            ElevatedButton.icon(
              icon: Icon(Icons.lock_open),
              label: Text('Decode Message'),
              onPressed: isLoading ? null : decodeMessage,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                padding: EdgeInsets.symmetric(vertical: 16),
              ),
            ),

            if (isLoading)
              Center(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: CircularProgressIndicator(),
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

## 🎯 Alur Kerja

### **Encode Flow:**
```
1. User pilih gambar dari gallery
2. User tulis pesan rahasia
3. Tap "Encode & Download"
   ↓
4. Flutter convert gambar ke base64
5. POST ke /api/stego/encode
   ↓
6. Server encode pesan ke gambar (LSB)
7. Return gambar hasil (base64)
   ↓
8. Flutter decode base64 → save ke Gallery
   📸 Lokasi: /storage/emulated/0/Pictures/stego_xxx.png (Android)
   📸 Lokasi: Photo Library (iOS)
9. User bisa lihat di Gallery dan share!
```

### **Decode Flow:**
```
1. User pilih gambar steganografi dari Gallery
2. Tap "Decode Message"
   ↓
3. Flutter convert gambar ke base64
4. POST ke /api/stego/decode
   ↓
5. Server extract pesan dari gambar (LSB)
6. Return pesan rahasia
   ↓
7. Flutter tampilkan pesan di dialog
```

### **📍 Lokasi File di HP:**

| Platform | Path | Akses |
|----------|------|-------|
| **Android** | `/storage/emulated/0/Pictures/stego_xxx.png` | ✅ Visible di Gallery app |
| **iOS** | Photo Library (managed by system) | ✅ Visible di Photos app |
| ~~App Private~~ | ~~`/data/.../app_flutter/`~~ | ❌ User tidak bisa akses |

**✅ Recommended:** Gunakan `image_gallery_saver` untuk simpan ke Gallery!

---

## ⚠️ IMPORTANT Notes

### 1. **Image Quality = 100%**
```dart
// ❌ WRONG - Compression akan rusak steganografi!
pickImage(imageQuality: 80);

// ✅ CORRECT - No compression
pickImage(imageQuality: 100);
```

### 2. **Format HARUS PNG!**
- Encode result: **Selalu PNG** (lossless)
- Decode input: **Harus PNG** (jangan JPEG!)
- JPEG compression akan **rusak** LSB steganography!

### 3. **No Storage on Server**
- Gambar **tidak** disimpan di server
- Pesan **tidak** disimpan di database
- Server hanya **process** lalu return result
- User **download sendiri** hasil encode

### 4. **Image Size Considerations**
- Gambar besar (4K) → base64 besar → upload/download lambat
- Recommended: Resize ke 1920x1080 atau lebih kecil
- Tapi ingat: Gambar kecil = kapasitas pesan kecil!

---

## 📊 Capacity Calculation

**Formula:**
```
Max Characters = (Width × Height × 3) / 8 - delimiter_length
```

**Examples:**
| Resolution | Total Pixels | Max Capacity |
|------------|--------------|--------------|
| 640×480 | 307,200 | ~115,000 chars |
| 1920×1080 | 2,073,600 | ~777,000 chars |
| 3840×2160 (4K) | 8,294,400 | ~3,110,000 chars |

**Tips:**
- Untuk pesan pendek (< 1000 chars): gambar kecil OK
- Untuk pesan panjang (> 10,000 chars): butuh gambar besar

---

## 🚀 Quick Start

### 1. Start Flask Server:
```bash
cd python
python main.py
```

### 2. Test dengan Postman:
```
POST http://localhost:5000/api/stego/encode
{
  "image_data": "<base64>",
  "secret_message": "Test!"
}
```

### 3. Integrate di Flutter:
- Copy code example di atas
- Add dependencies: `image_picker`, `http`, `path_provider`
- Run dan test!

---

## ✅ Advantages

✅ **Simple** - No database setup needed  
✅ **Privacy** - Nothing stored on server  
✅ **Fast** - Pure processing, no I/O  
✅ **Portable** - User own the encoded images  
✅ **Shareable** - Easy to share via WhatsApp, email, etc  

## ❌ Limitations

❌ **No History** - Tidak ada riwayat encode/decode  
❌ **No Gallery** - Tidak ada public gallery  
❌ **No User Management** - Tidak ada konsep ownership  
❌ **Upload Size** - Base64 images bisa sangat besar  

---

## 🎉 Summary

**Sekarang kamu punya:**
1. ✅ Encode API - Upload gambar + pesan → return hasil
2. ✅ Decode API - Upload gambar → return pesan
3. ✅ No database needed!
4. ✅ No file storage needed!
5. ✅ Flutter example ready!

**Perfect untuk:**
- Demo / POC (Proof of Concept)
- Privacy-focused app
- Simple steganography tool
- Learning purposes

Restart server dan test! 🚀
