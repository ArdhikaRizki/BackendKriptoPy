# 📨 Messaging API Documentation

API untuk fitur pengiriman pesan antar user (seperti email internal).

## 📋 Table of Contents
- [Endpoints](#endpoints)
- [Send Message](#1-send-message)
- [Get Inbox](#2-get-inbox)
- [Get Sent Messages](#3-get-sent-messages)
- [Get Message Detail](#4-get-message-detail)
- [Delete Message](#5-delete-message)
- [Get Conversation](#6-get-conversation)
- [Search Messages](#7-search-messages)
- [Error Handling](#error-handling)
- [Flutter Integration](#flutter-integration)

---

## 📌 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/messages/send` | Kirim pesan ke user lain |
| GET | `/api/messages/inbox` | Ambil pesan masuk (inbox) |
| GET | `/api/messages/sent` | Ambil pesan terkirim |
| GET | `/api/messages/<id>` | Ambil detail pesan |
| DELETE | `/api/messages/<id>` | Hapus pesan |
| GET | `/api/messages/conversation/<user_id>` | Ambil percakapan dengan user |
| GET | `/api/messages/search` | Cari pesan berdasarkan keyword |

---

## 1. Send Message

Kirim pesan ke user lain.

**Endpoint:** `POST /api/messages/send`

### Request Body
```json
{
  "sender_id": 1,
  "receiver_email": "user@example.com",
  "message_text": "Halo, ini pesan rahasia!"
}
```

### Response Success (201)
```json
{
  "success": true,
  "message": "Pesan berhasil dikirim ke username",
  "data": {
    "message_id": 123,
    "receiver_username": "username",
    "sent_at": "2025-11-01T10:30:00"
  }
}
```

### Response Error (400)
```json
{
  "success": false,
  "message": "Penerima tidak ditemukan"
}
```

### Postman Example
```bash
POST http://localhost:5000/api/messages/send
Content-Type: application/json

{
  "sender_id": 1,
  "receiver_email": "jane@example.com",
  "message_text": "Meeting hari ini jam 3 sore ya!"
}
```

---

## 2. Get Inbox

Ambil daftar pesan masuk (inbox).

**Endpoint:** `GET /api/messages/inbox`

### Query Parameters
- `user_id` (required): ID user
- `limit` (optional): Jumlah pesan, default 50
- `offset` (optional): Offset untuk pagination, default 0

### Request Example
```
GET http://localhost:5000/api/messages/inbox?user_id=1&limit=20&offset=0
```

### Response Success (200)
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": 123,
        "sender_id": 2,
        "sender_username": "john",
        "sender_email": "john@example.com",
        "message_text": "Halo! Apa kabar?",
        "created_at": "2025-11-01T10:30:00"
      },
      {
        "id": 122,
        "sender_id": 3,
        "sender_username": "alice",
        "sender_email": "alice@example.com",
        "message_text": "Meeting besok jam 2",
        "created_at": "2025-11-01T09:15:00"
      }
    ],
    "total": 100,
    "limit": 20,
    "offset": 0
  }
}
```

---

## 3. Get Sent Messages

Ambil daftar pesan terkirim.

**Endpoint:** `GET /api/messages/sent`

### Query Parameters
- `user_id` (required): ID user
- `limit` (optional): Jumlah pesan, default 50
- `offset` (optional): Offset untuk pagination, default 0

### Request Example
```
GET http://localhost:5000/api/messages/sent?user_id=1&limit=20&offset=0
```

### Response Success (200)
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": 125,
        "receiver_id": 2,
        "receiver_username": "jane",
        "receiver_email": "jane@example.com",
        "message_text": "Thanks for the info!",
        "created_at": "2025-11-01T11:00:00"
      }
    ],
    "total": 50,
    "limit": 20,
    "offset": 0
  }
}
```

---

## 4. Get Message Detail

Ambil detail pesan tertentu. User hanya bisa melihat pesan yang dia kirim atau terima.

**Endpoint:** `GET /api/messages/<message_id>`

### Query Parameters
- `user_id` (required): ID user yang mengakses

### Request Example
```
GET http://localhost:5000/api/messages/123?user_id=1
```

### Response Success (200)
```json
{
  "success": true,
  "data": {
    "id": 123,
    "sender_id": 2,
    "sender_username": "john",
    "sender_email": "john@example.com",
    "receiver_id": 1,
    "receiver_username": "jane",
    "receiver_email": "jane@example.com",
    "message_text": "Halo! Apa kabar?",
    "created_at": "2025-11-01T10:30:00"
  }
}
```

### Response Error (404)
```json
{
  "success": false,
  "message": "Pesan tidak ditemukan atau Anda tidak memiliki akses"
}
```

---

## 5. Delete Message

Hapus pesan tertentu. User hanya bisa menghapus pesan yang dia kirim atau terima.

**Endpoint:** `DELETE /api/messages/<message_id>`

### Request Body
```json
{
  "user_id": 1
}
```

### Response Success (200)
```json
{
  "success": true,
  "message": "Pesan berhasil dihapus"
}
```

### Response Error (404)
```json
{
  "success": false,
  "message": "Pesan tidak ditemukan atau Anda tidak memiliki akses"
}
```

### Postman Example
```bash
DELETE http://localhost:5000/api/messages/123
Content-Type: application/json

{
  "user_id": 1
}
```

---

## 6. Get Conversation

Ambil percakapan antara dua user.

**Endpoint:** `GET /api/messages/conversation/<other_user_id>`

### Query Parameters
- `user_id` (required): ID user yang mengakses
- `limit` (optional): Jumlah pesan, default 50

### Request Example
```
GET http://localhost:5000/api/messages/conversation/2?user_id=1&limit=50
```

### Response Success (200)
```json
{
  "success": true,
  "data": {
    "other_user": {
      "id": 2,
      "username": "john",
      "email": "john@example.com"
    },
    "messages": [
      {
        "id": 120,
        "sender_id": 1,
        "receiver_id": 2,
        "sender_username": "jane",
        "message_text": "Halo John!",
        "created_at": "2025-11-01T09:00:00",
        "direction": "sent"
      },
      {
        "id": 121,
        "sender_id": 2,
        "receiver_id": 1,
        "sender_username": "john",
        "message_text": "Halo Jane! Apa kabar?",
        "created_at": "2025-11-01T09:05:00",
        "direction": "received"
      }
    ],
    "total": 2
  }
}
```

---

## 7. Search Messages

Cari pesan berdasarkan keyword di isi pesan.

**Endpoint:** `GET /api/messages/search`

### Query Parameters
- `user_id` (required): ID user
- `keyword` (required): Kata kunci pencarian
- `limit` (optional): Jumlah hasil, default 50

### Request Example
```
GET http://localhost:5000/api/messages/search?user_id=1&keyword=meeting&limit=20
```

### Response Success (200)
```json
{
  "success": true,
  "data": {
    "keyword": "meeting",
    "results": [
      {
        "id": 122,
        "sender_id": 3,
        "sender_username": "alice",
        "receiver_id": 1,
        "receiver_username": "jane",
        "message_text": "Meeting besok jam 2 ya!",
        "created_at": "2025-11-01T09:15:00",
        "type": "received"
      }
    ],
    "total": 1
  }
}
```

---

## 🔴 Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "success": false,
  "message": "sender_id, receiver_email, dan message_text harus diisi"
}
```

#### 404 Not Found
```json
{
  "success": false,
  "message": "Pesan tidak ditemukan atau Anda tidak memiliki akses"
}
```

#### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Error: <error_details>"
}
```

---

## 📱 Flutter Integration

### 1. Create Message Model

```dart
class Message {
  final int id;
  final int senderId;
  final String senderUsername;
  final String? senderEmail;
  final int receiverId;
  final String? receiverUsername;
  final String? receiverEmail;
  final String messageText;
  final DateTime createdAt;
  final String? direction; // 'sent' or 'received'

  Message({
    required this.id,
    required this.senderId,
    required this.senderUsername,
    this.senderEmail,
    required this.receiverId,
    this.receiverUsername,
    this.receiverEmail,
    required this.messageText,
    required this.createdAt,
    this.direction,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      senderId: json['sender_id'],
      senderUsername: json['sender_username'],
      senderEmail: json['sender_email'],
      receiverId: json['receiver_id'],
      receiverUsername: json['receiver_username'],
      receiverEmail: json['receiver_email'],
      messageText: json['message_text'],
      createdAt: DateTime.parse(json['created_at']),
      direction: json['direction'],
    );
  }
}
```

### 2. Create Message Service

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class MessageService {
  final String baseUrl = 'http://localhost:5000/api/messages';

  // Send message
  Future<Map<String, dynamic>> sendMessage({
    required int senderId,
    required String receiverEmail,
    required String messageText,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/send'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'sender_id': senderId,
        'receiver_email': receiverEmail,
        'message_text': messageText,
      }),
    );

    return jsonDecode(response.body);
  }

  // Get inbox
  Future<List<Message>> getInbox({
    required int userId,
    int limit = 50,
    int offset = 0,
  }) async {
    final response = await http.get(
      Uri.parse('$baseUrl/inbox?user_id=$userId&limit=$limit&offset=$offset'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final messages = data['data']['messages'] as List;
      return messages.map((m) => Message.fromJson(m)).toList();
    }
    return [];
  }

  // Get sent messages
  Future<List<Message>> getSentMessages({
    required int userId,
    int limit = 50,
    int offset = 0,
  }) async {
    final response = await http.get(
      Uri.parse('$baseUrl/sent?user_id=$userId&limit=$limit&offset=$offset'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final messages = data['data']['messages'] as List;
      return messages.map((m) => Message.fromJson(m)).toList();
    }
    return [];
  }

  // Get conversation
  Future<List<Message>> getConversation({
    required int userId,
    required int otherUserId,
    int limit = 50,
  }) async {
    final response = await http.get(
      Uri.parse('$baseUrl/conversation/$otherUserId?user_id=$userId&limit=$limit'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final messages = data['data']['messages'] as List;
      return messages.map((m) => Message.fromJson(m)).toList();
    }
    return [];
  }

  // Delete message
  Future<bool> deleteMessage({
    required int messageId,
    required int userId,
  }) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/$messageId'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId}),
    );

    final data = jsonDecode(response.body);
    return data['success'] ?? false;
  }

  // Search messages
  Future<List<Message>> searchMessages({
    required int userId,
    required String keyword,
    int limit = 50,
  }) async {
    final response = await http.get(
      Uri.parse('$baseUrl/search?user_id=$userId&keyword=$keyword&limit=$limit'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final messages = data['data']['results'] as List;
      return messages.map((m) => Message.fromJson(m)).toList();
    }
    return [];
  }
}
```

### 3. Example Usage - Send Message Screen

```dart
class SendMessageScreen extends StatefulWidget {
  final int currentUserId;

  const SendMessageScreen({required this.currentUserId});

  @override
  State<SendMessageScreen> createState() => _SendMessageScreenState();
}

class _SendMessageScreenState extends State<SendMessageScreen> {
  final _receiverController = TextEditingController();
  final _messageController = TextEditingController();
  final _messageService = MessageService();
  bool _isLoading = false;

  Future<void> _sendMessage() async {
    if (_receiverController.text.isEmpty || _messageController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Email penerima dan pesan harus diisi')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final result = await _messageService.sendMessage(
        senderId: widget.currentUserId,
        receiverEmail: _receiverController.text,
        messageText: _messageController.text,
      );

      if (result['success']) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(result['message'])),
        );
        _messageController.clear();
        _receiverController.clear();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(result['message'])),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Kirim Pesan')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _receiverController,
              decoration: InputDecoration(
                labelText: 'Email Penerima',
                hintText: 'user@example.com',
              ),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _messageController,
              decoration: InputDecoration(
                labelText: 'Pesan',
                hintText: 'Tulis pesan Anda...',
              ),
              maxLines: 5,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isLoading ? null : _sendMessage,
              child: _isLoading
                  ? CircularProgressIndicator()
                  : Text('Kirim Pesan'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### 4. Example Usage - Inbox Screen

```dart
class InboxScreen extends StatefulWidget {
  final int currentUserId;

  const InboxScreen({required this.currentUserId});

  @override
  State<InboxScreen> createState() => _InboxScreenState();
}

class _InboxScreenState extends State<InboxScreen> {
  final _messageService = MessageService();
  List<Message> _messages = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadInbox();
  }

  Future<void> _loadInbox() async {
    setState(() => _isLoading = true);
    try {
      final messages = await _messageService.getInbox(
        userId: widget.currentUserId,
      );
      setState(() => _messages = messages);
    } catch (e) {
      print('Error: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Inbox')),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : _messages.isEmpty
              ? Center(child: Text('Tidak ada pesan'))
              : ListView.builder(
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final message = _messages[index];
                    return ListTile(
                      leading: CircleAvatar(
                        child: Text(message.senderUsername[0].toUpperCase()),
                      ),
                      title: Text(message.senderUsername),
                      subtitle: Text(
                        message.messageText,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      trailing: Text(
                        _formatDate(message.createdAt),
                        style: TextStyle(fontSize: 12),
                      ),
                      onTap: () {
                        // Navigate to message detail
                      },
                    );
                  },
                ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SendMessageScreen(
                currentUserId: widget.currentUserId,
              ),
            ),
          );
        },
        child: Icon(Icons.edit),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inDays == 0) {
      return '${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } else if (diff.inDays == 1) {
      return 'Kemarin';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }
}
```

---

## 🎯 Features Summary

✅ **Send Message** - Kirim pesan ke user lain via email  
✅ **Inbox** - Lihat pesan masuk dengan pagination  
✅ **Sent Messages** - Lihat pesan terkirim  
✅ **Message Detail** - Lihat detail pesan lengkap  
✅ **Delete Message** - Hapus pesan (sender atau receiver)  
✅ **Conversation** - Lihat percakapan dengan user tertentu  
✅ **Search** - Cari pesan berdasarkan keyword  
✅ **Privacy** - User hanya bisa akses pesan mereka sendiri  
✅ **Pagination** - Support limit & offset  

---

## 💡 Tips

1. **Enkripsi Pesan**: Gunakan steganography untuk menyembunyikan pesan dalam gambar
2. **Attachment**: Tabel `message_attachments` sudah siap untuk fitur attachment
3. **Real-time**: Bisa ditambahkan WebSocket untuk real-time messaging
4. **Read Status**: Bisa ditambahkan kolom `is_read` di tabel messages
5. **Soft Delete**: Bisa ditambahkan kolom `deleted_at` untuk soft delete

---

## 🔗 Related APIs

- [Authentication API](README_MD5.md) - Login & Register
- [Steganography API](README_STATELESS_STEGO.md) - Encode & Decode
- [Error Handling](ERROR_HANDLING.md) - Error handling guide
