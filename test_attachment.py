"""
Test Script untuk Debug Attachment Insert
"""

from connection import get_db_connection
from config import config
from message_service import MessageService

# Setup
db = get_db_connection(**config.get_db_config())
message_service = MessageService(db)

# Test data (ganti dengan message_id yang valid dari database kamu)
test_message_id = 1  # Ganti dengan ID message yang ada di database
test_filename = "test_debug.pdf"
test_file_path = "uploads/message_attachments/test_debug.pdf"
test_file_type = "document"
test_file_size = 12345

print("\n" + "="*60)
print("🧪 TESTING add_attachment() Function")
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
print("🔍 Verifying in Database...")
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
