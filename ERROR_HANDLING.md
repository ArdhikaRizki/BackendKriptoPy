# 🔍 Error Handling - Steganography API

## Decode Error Responses

### ✅ **Success Response**
```json
{
  "success": true,
  "message": "Pesan berhasil diekstrak",
  "data": {
    "secret_message": "Ini pesan rahasia!",
    "message_length": 18,
    "image_info": {
      "width": 1920,
      "height": 1080,
      "total_pixels": 2073600,
      "max_capacity": 777591
    }
  }
}
```

---

## ❌ **Error Responses**

### 1. **Gambar Tidak Mengandung Pesan** (400)

**Scenario:** Upload gambar biasa (bukan hasil encode)

**Response:**
```json
{
  "success": false,
  "error_type": "NO_MESSAGE_FOUND",
  "message": "Gambar ini tidak mengandung pesan steganografi",
  "details": "Delimiter tidak ditemukan. Pastikan gambar yang diupload sudah di-encode dengan aplikasi ini.",
  "suggestion": "Gunakan gambar yang sudah di-encode dengan endpoint /api/stego/encode"
}
```

**Penyebab:**
- Gambar asli (belum di-encode)
- Gambar di-encode dengan tool lain (beda delimiter)
- Gambar hasil JPEG compression (LSB rusak)

**Solusi:**
- Upload gambar yang sudah di-encode dengan `/api/stego/encode`
- Pastikan format PNG (jangan JPEG!)
- Jangan compress/resize gambar setelah encode

---

### 2. **Invalid Base64** (500)

**Scenario:** Base64 string tidak valid

**Response:**
```json
{
  "success": false,
  "error_type": "DECODE_ERROR",
  "message": "Error saat decoding: Incorrect padding"
}
```

**Penyebab:**
- Base64 string corrupt/incomplete
- Prefix `data:image/...;base64,` tidak di-strip

**Solusi:**
- Pastikan base64 string valid
- Hapus prefix jika ada

---

### 3. **Invalid Image Format** (500)

**Scenario:** File bukan gambar atau format tidak didukung

**Response:**
```json
{
  "success": false,
  "error_type": "DECODE_ERROR",
  "message": "Error saat decoding: cannot identify image file"
}
```

**Penyebab:**
- File bukan gambar (PDF, video, dll)
- Format rusak/corrupt

**Solusi:**
- Upload file gambar valid (PNG, JPG, BMP)
- Pastikan file tidak corrupt

---

### 4. **Missing image_data** (400)

**Scenario:** Request body tidak ada `image_data`

**Response:**
```json
{
  "success": false,
  "message": "image_data harus diisi"
}
```

**Solusi:**
- Tambahkan field `image_data` di request body

---

## 🧪 **Testing Error Cases**

### Test 1: Gambar Biasa (No Message)
```bash
# Upload gambar asli (belum di-encode)
curl -X POST http://localhost:5000/api/stego/decode \
  -H "Content-Type: application/json" \
  -d '{"image_data":"<base64 gambar biasa>"}'

# Expected: 400 - NO_MESSAGE_FOUND
```

### Test 2: Invalid Base64
```bash
curl -X POST http://localhost:5000/api/stego/decode \
  -H "Content-Type: application/json" \
  -d '{"image_data":"invalid_base64_string!!!"}'

# Expected: 500 - DECODE_ERROR
```

### Test 3: Missing Field
```bash
curl -X POST http://localhost:5000/api/stego/decode \
  -H "Content-Type: application/json" \
  -d '{}'

# Expected: 400 - image_data harus diisi
```

---

## 💻 **Flutter Error Handling**

```dart
Future<String> decodeMessage(String base64Image) async {
  try {
    final response = await http.post(
      Uri.parse('$baseUrl/api/stego/decode'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'image_data': base64Image}),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200 && data['success'] == true) {
      return data['data']['secret_message'];
    } else {
      // Handle different error types
      final errorType = data['error_type'];
      
      switch (errorType) {
        case 'NO_MESSAGE_FOUND':
          throw StegoException(
            'Gambar tidak mengandung pesan tersembunyi',
            suggestion: data['suggestion'],
          );
        
        case 'DECODE_ERROR':
          throw StegoException(
            'Gagal decode gambar',
            details: data['message'],
          );
        
        default:
          throw StegoException(data['message']);
      }
    }
  } catch (e) {
    if (e is StegoException) rethrow;
    throw StegoException('Network error: $e');
  }
}

// Custom Exception Class
class StegoException implements Exception {
  final String message;
  final String? suggestion;
  final String? details;

  StegoException(this.message, {this.suggestion, this.details});

  @override
  String toString() {
    var msg = 'StegoException: $message';
    if (details != null) msg += '\nDetails: $details';
    if (suggestion != null) msg += '\nSuggestion: $suggestion';
    return msg;
  }
}

// Usage in UI
try {
  final message = await decodeMessage(base64Image);
  showDialog(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('Secret Message'),
      content: Text(message),
    ),
  );
} on StegoException catch (e) {
  showDialog(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('Error'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(e.message),
          if (e.suggestion != null) ...[
            SizedBox(height: 8),
            Text(
              'Saran: ${e.suggestion}',
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
          ],
        ],
      ),
    ),
  );
} catch (e) {
  showDialog(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('Unexpected Error'),
      content: Text(e.toString()),
    ),
  );
}
```

---

## 🎯 **Summary Error Types**

| Error Type | HTTP Code | Cause | Solution |
|------------|-----------|-------|----------|
| `NO_MESSAGE_FOUND` | 400 | Gambar bukan stego | Upload gambar hasil encode |
| `DECODE_ERROR` | 500 | Base64/image invalid | Check format & base64 |
| Missing `image_data` | 400 | Request incomplete | Add `image_data` field |

---

## 🔧 **Debugging Tips**

### 1. **Check Delimiter**
```python
# Di steganography.py
self.delimiter = "###END###"  # Default delimiter
```

Jika gambar di-encode dengan delimiter berbeda, tidak akan ketemu!

### 2. **Check Image Format**
```python
# Pastikan PNG (lossless)
if image_format != 'PNG':
    print("WARNING: Format bukan PNG, LSB mungkin rusak!")
```

### 3. **Limit Characters Read**
```python
# Sudah ada safety limit 10000 chars
max_chars = 10000  # Prevent infinite loop
```

Ini mencegah decode terus-menerus jika delimiter tidak ketemu.

---

## ✅ **Best Practices**

1. ✅ **Always use PNG** - Jangan JPEG!
2. ✅ **Check error_type** - Handle berbeda untuk tiap error
3. ✅ **Show user-friendly messages** - Jangan langsung show technical error
4. ✅ **Test with non-stego images** - Pastikan error handling bekerja
5. ✅ **Validate before decode** - Check format dan size dulu

🎉 **Done!**
