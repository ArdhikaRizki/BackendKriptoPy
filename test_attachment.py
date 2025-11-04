"""
Test Script untuk Debug Attachment Insert
"""

from connection import get_db_connection
from config import config
from message_service import MessageService

# Setup
db = get_db_connection(**config.get_db_config())
message_service = MessageService(db)

print("\n" + "="*60)
print("🔍 Step 1: Cari message ID yang VALID")
print("="*60)

# Cari message yang ada di database
check_query = "SELECT id, sender_id, receiver_id, created_at FROM messages ORDER BY id DESC LIMIT 5"
messages = db.execute_read_dict(check_query)

if not messages or len(messages) == 0:
    print("❌ TIDAK ADA MESSAGE di database!")
    print("   Silakan kirim message dulu lewat API /api/messages/send")
    db.disconnect()
    exit(1)

print(f"✅ Ditemukan {len(messages)} message di database:")
for msg in messages:
    print(f"   ID={msg['id']}, sender={msg['sender_id']}, receiver={msg['receiver_id']}, created={msg['created_at']}")

# Ambil ID message terbaru
test_message_id = messages[0]['id']
print(f"\n✅ Akan test dengan message_id = {test_message_id}")

# Test data
test_filename = "test_debug.pdf"
test_file_path = "uploads/message_attachments/test_debug.pdf"
test_file_type = "document"
test_file_size = 12345

print("\n" + "="*60)
print("🧪 Step 2: Testing add_attachment() Function")
print("="*60)

# Call add_attachment
attachment_id = message_service.add_attachment(
    message_id=test_message_id,
    filename=test_filename,
    file_path=test_file_path,
    file_type=test_file_type,
    file_size=test_file_size
)

print("\n" + "="*60)
print(f"📊 RESULT: attachment_id = {attachment_id}")
print("="*60)

if attachment_id:
    print("✅ SUCCESS! Data masuk ke database!")
    print(f"   Check table: SELECT * FROM message_attachments WHERE id={attachment_id}")
else:
    print("❌ FAILED! Data TIDAK masuk ke database!")
    print("   Check error messages above ^^^")

# Verify di database
print("\n" + "="*60)
print("🔍 Step 3: Verifying in Database...")
print("="*60)

verify_query = "SELECT * FROM message_attachments ORDER BY id DESC LIMIT 5"
results = db.execute_read_dict(verify_query)

if results:
    print(f"✅ Found {len(results)} recent attachments in database:")
    for row in results:
        print(f"   ID={row['id']}, message_id={row['message_id']}, filename={row['filename']}")
else:
    print("❌ NO attachments found in database!")

db.disconnect()
print("\n✅ Test complete!\n")
