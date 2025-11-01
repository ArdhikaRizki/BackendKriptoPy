"""
Vigenere Cipher - Simple Implementation
Enkripsi dengan menggunakan keyword
"""


def vigenere_encrypt(text, key):
    """
    Enkripsi text dengan Vigenere Cipher.
    
    Args:
        text: Text yang akan dienkripsi
        key: Keyword untuk enkripsi
    
    Returns:
        Text terenkripsi
    
    Example:
        >>> vigenere_encrypt("HELLO", "KEY")
        'RIJVS'
    """
    result = ""
    key = key.upper()
    key_index = 0
    
    for char in text:
        if char.isupper():
            shift = ord(key[key_index % len(key)]) - 65
            result += chr((ord(char) - 65 + shift) % 26 + 65)
            key_index += 1
        elif char.islower():
            shift = ord(key[key_index % len(key)]) - 65
            result += chr((ord(char) - 97 + shift) % 26 + 97)
            key_index += 1
        else:
            result += char
    
    return result


def vigenere_decrypt(text, key):
    """
    Dekripsi text dengan Vigenere Cipher.
    
    Args:
        text: Text yang akan didekripsi
        key: Keyword untuk dekripsi
    
    Returns:
        Text terdekripsi
    
    Example:
        >>> vigenere_decrypt("RIJVS", "KEY")
        'HELLO'
    """
    result = ""
    key = key.upper()
    key_index = 0
    
    for char in text:
        if char.isupper():
            shift = ord(key[key_index % len(key)]) - 65
            result += chr((ord(char) - 65 - shift + 26) % 26 + 65)
            key_index += 1
        elif char.islower():
            shift = ord(key[key_index % len(key)]) - 65
            result += chr((ord(char) - 97 - shift + 26) % 26 + 97)
            key_index += 1
        else:
            result += char
    
    return result


# Testing
if __name__ == "__main__":
    print("=== VIGENERE CIPHER ===\n")
    
    # Test 1
    plaintext = "HELLO WORLD"
    key = "KEY"
    encrypted = vigenere_encrypt(plaintext, key)
    decrypted = vigenere_decrypt(encrypted, key)
    
    print(f"Plaintext:  {plaintext}")
    print(f"Key:        {key}")
    print(f"Encrypted:  {encrypted}")
    print(f"Decrypted:  {decrypted}")
    print(f"Match: {decrypted == plaintext} ✓")
    
    # Test 2 - Mixed case
    text2 = "Hello World!"
    key2 = "SECRET"
    enc2 = vigenere_encrypt(text2, key2)
    dec2 = vigenere_decrypt(enc2, key2)
    
    print(f"\nPlaintext:  {text2}")
    print(f"Key:        {key2}")
    print(f"Encrypted:  {enc2}")
    print(f"Decrypted:  {dec2}")
    print(f"Match: {dec2 == text2} ✓")
