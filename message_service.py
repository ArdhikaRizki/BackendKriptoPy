"""
Message Service Module
Modul untuk mengelola fitur pengiriman pesan antar user (seperti email internal)
Dengan enkripsi DES untuk keamanan pesan
"""

from datetime import datetime
from utils.des_encryption import DESEncryption
import json


class MessageService:
    """Service untuk mengelola pengiriman dan penerimaan pesan dengan DES encryption."""

    def __init__(self, db_connection, encryption_key="msg12345"):
        """
        Inisialisasi MessageService.
        
        Args:
            db_connection: Database connection object dari connection.py
            encryption_key: Key untuk DES encryption (8 karakter, default: "msg12345")
        """
        self.db = db_connection
        self.des = DESEncryption(encryption_key)

    def send_message(self, sender_id, receiver_email, message_text):
        """
        Kirim pesan dari sender ke receiver dengan enkripsi DES.
        
        Args:
            sender_id: ID user pengirim
            receiver_email: Email user penerima
            message_text: Isi pesan plaintext (akan dienkripsi dengan DES)
        
        Returns:
            Dictionary dengan status dan message
        """
        # Validasi pesan tidak boleh kosong
        if not message_text or message_text.strip() == "":
            return {
                'success': False,
                'message': 'Pesan tidak boleh kosong'
            }

        # Cari receiver berdasarkan email
        receiver_query = "SELECT id, username FROM users WHERE email = %s"
        receiver = self.db.execute_read_dict(receiver_query, (receiver_email,))

        if not receiver:
            return {
                'success': False,
                'message': 'Penerima tidak ditemukan'
            }

        receiver_id = receiver[0]['id']
        receiver_username = receiver[0]['username']

        # Cek sender tidak mengirim ke diri sendiri
        if sender_id == receiver_id:
            return {
                'success': False,
                'message': 'Tidak bisa mengirim pesan ke diri sendiri'
            }

        # 🔐 ENKRIPSI PESAN DENGAN DES
        encrypted_result = self.des.encrypt(message_text)
        
        # Simpan ciphertext dan IV sebagai JSON
        encrypted_data = json.dumps({
            'ciphertext': encrypted_result['ciphertext'],
            'iv': encrypted_result['iv']
        })

        # Insert pesan terenkripsi ke database
        insert_query = """
        INSERT INTO messages (sender_id, receiver_id, message_text) 
        VALUES (%s, %s, %s)
        """

        success = self.db.execute_query(insert_query, (sender_id, receiver_id, encrypted_data))

        if success:
            # Ambil ID pesan yang baru dibuat
            message_id_query = "SELECT LAST_INSERT_ID() as message_id"
            result = self.db.execute_read_dict(message_id_query)
            message_id = result[0]['message_id'] if result else None

            return {
                'success': True,
                'message': f'Pesan berhasil dikirim ke {receiver_username} (encrypted with DES)',
                'data': {
                    'message_id': message_id,
                    'receiver_username': receiver_username,
                    'sent_at': datetime.now().isoformat(),
                    'encrypted': True
                }
            }
        else:
            return {
                'success': False,
                'message': 'Gagal mengirim pesan'
            }

    def get_inbox(self, user_id, limit=50, offset=0):
        """
        Ambil daftar pesan yang diterima user dan decrypt dengan DES.
        
        Args:
            user_id: ID user penerima
            limit: Jumlah maksimal pesan yang ditampilkan (default: 50)
            offset: Offset untuk pagination (default: 0)
        
        Returns:
            Dictionary dengan status dan list pesan (decrypted)
        """
        query = """
        SELECT 
            m.id,
            m.sender_id,
            u.username as sender_username,
            u.email as sender_email,
            m.message_text,
            m.created_at
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.receiver_id = %s
        ORDER BY m.created_at DESC
        LIMIT %s OFFSET %s
        """

        messages = self.db.execute_read_dict(query, (user_id, limit, offset))

        # 🔓 DEKRIPSI SETIAP PESAN + AMBIL ATTACHMENTS
        if messages:
            for msg in messages:
                msg['message_text'] = self._decrypt_message(msg['message_text'])
                
                # Get attachments untuk message ini
                att_query = """
                SELECT id, filename, file_type, file_size
                FROM message_attachments
                WHERE message_id = %s
                """
                attachments = self.db.execute_read_dict(att_query, (msg['id'],))
                
                if attachments:
                    for att in attachments:
                        att['download_url'] = f"/api/messages/attachments/{att['id']}"
                    msg['attachments'] = attachments
                else:
                    msg['attachments'] = []

        # Hitung total pesan
        count_query = "SELECT COUNT(*) as total FROM messages WHERE receiver_id = %s"
        count_result = self.db.execute_read_dict(count_query, (user_id,))
        total = count_result[0]['total'] if count_result else 0

        return {
            'success': True,
            'data': {
                'messages': messages if messages else [],
                'total': total,
                'limit': limit,
                'offset': offset
            }
        }

    def get_sent_messages(self, user_id, limit=50, offset=0):
        """
        Ambil daftar pesan yang dikirim user dan decrypt dengan DES.
        
        Args:
            user_id: ID user pengirim
            limit: Jumlah maksimal pesan yang ditampilkan (default: 50)
            offset: Offset untuk pagination (default: 0)
        
        Returns:
            Dictionary dengan status dan list pesan (decrypted)
        """
        query = """
        SELECT 
            m.id,
            m.receiver_id,
            u.username as receiver_username,
            u.email as receiver_email,
            m.message_text,
            m.created_at
        FROM messages m
        JOIN users u ON m.receiver_id = u.id
        WHERE m.sender_id = %s
        ORDER BY m.created_at DESC
        LIMIT %s OFFSET %s
        """

        messages = self.db.execute_read_dict(query, (user_id, limit, offset))

        # 🔓 DEKRIPSI SETIAP PESAN
        if messages:
            for msg in messages:
                msg['message_text'] = self._decrypt_message(msg['message_text'])

        # Hitung total pesan
        count_query = "SELECT COUNT(*) as total FROM messages WHERE sender_id = %s"
        count_result = self.db.execute_read_dict(count_query, (user_id,))
        total = count_result[0]['total'] if count_result else 0

        return {
            'success': True,
            'data': {
                'messages': messages if messages else [],
                'total': total,
                'limit': limit,
                'offset': offset
            }
        }

    def get_message_detail(self, message_id, user_id):
        """
        Ambil detail pesan tertentu dan decrypt dengan DES.
        User hanya bisa melihat pesan yang dia kirim atau terima.
        
        Args:
            message_id: ID pesan
            user_id: ID user yang mengakses
        
        Returns:
            Dictionary dengan status dan detail pesan (decrypted)
        """
        query = """
        SELECT 
            m.id,
            m.sender_id,
            sender.username as sender_username,
            sender.email as sender_email,
            m.receiver_id,
            receiver.username as receiver_username,
            receiver.email as receiver_email,
            m.message_text,
            m.created_at
        FROM messages m
        JOIN users sender ON m.sender_id = sender.id
        JOIN users receiver ON m.receiver_id = receiver.id
        WHERE m.id = %s AND (m.sender_id = %s OR m.receiver_id = %s)
        """

        result = self.db.execute_read_dict(query, (message_id, user_id, user_id))

        if not result:
            return {
                'success': False,
                'message': 'Pesan tidak ditemukan atau Anda tidak memiliki akses'
            }

        # 🔓 DEKRIPSI PESAN + AMBIL ATTACHMENTS
        message_data = result[0]
        message_data['message_text'] = self._decrypt_message(message_data['message_text'])
        
        # Get attachments
        att_query = """
        SELECT id, filename, file_type, file_size
        FROM message_attachments
        WHERE message_id = %s
        """
        attachments = self.db.execute_read_dict(att_query, (message_id,))
        
        if attachments:
            for att in attachments:
                att['download_url'] = f"/api/messages/attachments/{att['id']}"
            message_data['attachments'] = attachments
        else:
            message_data['attachments'] = []

        return {
            'success': True,
            'data': message_data
        }

    def delete_message(self, message_id, user_id):
        """
        Hapus pesan tertentu.
        User hanya bisa menghapus pesan yang dia kirim atau terima.
        
        Args:
            message_id: ID pesan
            user_id: ID user yang menghapus
        
        Returns:
            Dictionary dengan status dan message
        """
        # Cek apakah pesan ada dan user memiliki akses
        check_query = """
        SELECT id FROM messages 
        WHERE id = %s AND (sender_id = %s OR receiver_id = %s)
        """
        result = self.db.execute_read_dict(check_query, (message_id, user_id, user_id))

        if not result:
            return {
                'success': False,
                'message': 'Pesan tidak ditemukan atau Anda tidak memiliki akses'
            }

        # Hapus attachments terlebih dahulu (files + DB)
        self.delete_attachments(message_id)

        # Hapus pesan
        delete_query = "DELETE FROM messages WHERE id = %s"
        success = self.db.execute_query(delete_query, (message_id,))

        if success:
            return {
                'success': True,
                'message': 'Pesan berhasil dihapus'
            }
        else:
            return {
                'success': False,
                'message': 'Gagal menghapus pesan'
            }

    def get_conversation(self, user_id, other_user_id, limit=50):
        """
        Ambil percakapan antara dua user dan decrypt dengan DES.
        
        Args:
            user_id: ID user yang mengakses
            other_user_id: ID user lawan bicara
            limit: Jumlah maksimal pesan (default: 50)
        
        Returns:
            Dictionary dengan status dan list pesan (decrypted)
        """
        query = """
        SELECT 
            m.id,
            m.sender_id,
            m.receiver_id,
            sender.username as sender_username,
            m.message_text,
            m.created_at,
            CASE 
                WHEN m.sender_id = %s THEN 'sent'
                ELSE 'received'
            END as direction
        FROM messages m
        JOIN users sender ON m.sender_id = sender.id
        WHERE 
            (m.sender_id = %s AND m.receiver_id = %s) OR 
            (m.sender_id = %s AND m.receiver_id = %s)
        ORDER BY m.created_at ASC
        LIMIT %s
        """

        messages = self.db.execute_read_dict(
            query, 
            (user_id, user_id, other_user_id, other_user_id, user_id, limit)
        )

        # 🔓 DEKRIPSI SETIAP PESAN
        if messages:
            for msg in messages:
                msg['message_text'] = self._decrypt_message(msg['message_text'])

        # Ambil info user lawan bicara
        other_user_query = "SELECT username, email FROM users WHERE id = %s"
        other_user = self.db.execute_read_dict(other_user_query, (other_user_id,))

        if not other_user:
            return {
                'success': False,
                'message': 'User tidak ditemukan'
            }

        return {
            'success': True,
            'data': {
                'other_user': {
                    'id': other_user_id,
                    'username': other_user[0]['username'],
                    'email': other_user[0]['email']
                },
                'messages': messages if messages else [],
                'total': len(messages) if messages else 0
            }
        }

    def search_messages(self, user_id, keyword, limit=50):
        """
        Cari pesan berdasarkan keyword (search pada plaintext setelah decrypt).
        
        Note: Karena pesan terenkripsi, search dilakukan setelah decrypt semua pesan.
        Untuk database besar, ini bisa lambat. Consider indexing atau full-text search.
        
        Args:
            user_id: ID user yang mencari
            keyword: Kata kunci pencarian
            limit: Jumlah maksimal hasil (default: 50)
        
        Returns:
            Dictionary dengan status dan hasil pencarian
        """
        # Ambil semua pesan user (encrypted)
        query = """
        SELECT 
            m.id,
            m.sender_id,
            sender.username as sender_username,
            m.receiver_id,
            receiver.username as receiver_username,
            m.message_text,
            m.created_at,
            CASE 
                WHEN m.sender_id = %s THEN 'sent'
                ELSE 'received'
            END as type
        FROM messages m
        JOIN users sender ON m.sender_id = sender.id
        JOIN users receiver ON m.receiver_id = receiver.id
        WHERE 
            (m.sender_id = %s OR m.receiver_id = %s)
        ORDER BY m.created_at DESC
        """

        all_messages = self.db.execute_read_dict(query, (user_id, user_id, user_id))

        # 🔓 DEKRIPSI DAN FILTER BERDASARKAN KEYWORD
        results = []
        keyword_lower = keyword.lower()
        
        if all_messages:
            for msg in all_messages:
                decrypted_text = self._decrypt_message(msg['message_text'])
                msg['message_text'] = decrypted_text
                
                # Cek apakah keyword ada di pesan
                if keyword_lower in decrypted_text.lower():
                    results.append(msg)
                    
                    # Stop jika sudah mencapai limit
                    if len(results) >= limit:
                        break

        return {
            'success': True,
            'data': {
                'keyword': keyword,
                'results': results,
                'total': len(results)
            }
        }

    def add_attachment(self, message_id, filename, file_path, file_type, file_size):
        """
        Simpan metadata attachment ke database.
        
        Args:
            message_id: ID pesan
            filename: Nama file original
            file_path: Path file di server
            file_type: Tipe file (image, document, dll)
            file_size: Ukuran file (bytes)
        
        Returns:
            ID attachment yang baru dibuat
        """
        query = """
        INSERT INTO message_attachments 
        (message_id, filename, file_path, file_type, file_size, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """
        
        result = self.db.execute_write_query(
            query, 
            (message_id, filename, file_path, file_type, file_size)
        )
        
        # Get last insert ID
        last_id_query = "SELECT LAST_INSERT_ID() as id"
        last_id = self.db.execute_read_dict(last_id_query)
        
        if last_id:
            return last_id[0]['id']
        return None

    def get_attachment(self, attachment_id, user_id):
        """
        Ambil info attachment dengan validasi akses (hanya sender/receiver).
        
        Args:
            attachment_id: ID attachment
            user_id: ID user yang akses
        
        Returns:
            Dictionary attachment info atau None jika tidak ada akses
        """
        query = """
        SELECT 
            a.id,
            a.message_id,
            a.filename,
            a.file_path,
            a.file_type,
            a.file_size,
            a.created_at,
            m.sender_id,
            m.receiver_id
        FROM message_attachments a
        JOIN messages m ON a.message_id = m.id
        WHERE 
            a.id = %s
            AND (m.sender_id = %s OR m.receiver_id = %s)
        """
        
        result = self.db.execute_read_dict(query, (attachment_id, user_id, user_id))
        
        if result:
            return result[0]
        return None

    def delete_attachments(self, message_id):
        """
        Hapus semua attachment dari pesan (file + database).
        
        Args:
            message_id: ID pesan
        """
        import os
        
        # Get all attachments
        query = "SELECT file_path FROM message_attachments WHERE message_id = %s"
        attachments = self.db.execute_read_dict(query, (message_id,))
        
        # Delete files from disk
        if attachments:
            for att in attachments:
                file_path = att['file_path']
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"🗑️ Deleted file: {file_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to delete file {file_path}: {e}")
        
        # Delete from database
        delete_query = "DELETE FROM message_attachments WHERE message_id = %s"
        self.db.execute_write_query(delete_query, (message_id,))

    def _decrypt_message(self, encrypted_data):
        """
        Helper function untuk decrypt pesan dari database.
        
        Args:
            encrypted_data: JSON string dengan ciphertext dan IV
        
        Returns:
            Plaintext message (string)
        """
        try:
            # Parse JSON
            data = json.loads(encrypted_data)
            ciphertext = data['ciphertext']
            iv = data['iv']
            
            # Decrypt dengan DES
            plaintext = self.des.decrypt(ciphertext, iv)
            return plaintext
        except Exception as e:
            # Jika gagal decrypt (misal: data lama yang belum terenkripsi)
            print(f"⚠️ Decrypt error: {e}")
            return encrypted_data  # Return as-is


# Testing
if __name__ == "__main__":
    from connection import DatabaseConnection
    
    print("=== Test Message Service ===\n")
    print("Koneksi ke database untuk testing...")
    
    # Catatan: Untuk testing, pastikan database sudah ada
    # dan tabel messages sudah dibuat
