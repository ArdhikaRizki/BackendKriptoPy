"""
Caesar Cipher - Simple Implementation
Enkripsi dengan menggeser huruf sejumlah posisi tertentu
"""


def caesar_encrypt(text, shift=3):
    """
    Enkripsi text dengan Caesar Cipher.
    
    Args:
        text: Text yang akan dienkripsi
        shift: Jumlah pergeseran (default: 3)
    
    Returns:
        Text terenkripsi
    
    Example:
        >>> caesar_encrypt("HELLO", 3)
        'KHOOR'
    """
    result = ""
    
    for char in text:
        if char.isupper():
            result += chr((ord(char) - 65 + shift) % 26 + 65)
        elif char.islower():
            result += chr((ord(char) - 97 + shift) % 26 + 97)
        else:
            result += char
    
    return result


def caesar_decrypt(text, shift=3):
    """
    Dekripsi text dengan Caesar Cipher.
    
    Args:
        text: Text yang akan didekripsi
        shift: Jumlah pergeseran (default: 3)
    
    Returns:
        Text terdekripsi
    
    Example:
        >>> caesar_decrypt("KHOOR", 3)
        'HELLO'
    """
    return caesar_encrypt(text, -shift)


# Testing
if __name__ == "__main__":
    print("=== CAESAR CIPHER ===\n")
    
    # Test 1
    plaintext = "HELLO WORLD"
    encrypted = caesar_encrypt(plaintext, 3)
    decrypted = caesar_decrypt(encrypted, 3)
    
    print(f"Plaintext:  {plaintext}")
    print(f"Encrypted:  {encrypted}")
    print(f"Decrypted:  {decrypted}")
    print(f"Match: {decrypted == plaintext} ✓")
    
    # Test 2 - Mixed case
    text2 = "Hello World 123!"
    enc2 = caesar_encrypt(text2, 5)
    dec2 = caesar_decrypt(enc2, 5)
    
    print(f"\nPlaintext:  {text2}")
    print(f"Encrypted:  {enc2}")
    print(f"Decrypted:  {dec2}")
    print(f"Match: {dec2 == text2} ✓")
