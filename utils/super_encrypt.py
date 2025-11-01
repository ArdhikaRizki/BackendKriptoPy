"""
Super Encrypt - Triple Layer Encryption
Menggabungkan 3 algoritma: Caesar → Vigenere → DES

Flow Encryption:
1. Plaintext → Caesar Cipher (shift key)
2. Caesar result → Vigenere Cipher (keyword)
3. Vigenere result → DES Encryption (DES key)

Flow Decryption (reverse):
1. Ciphertext → DES Decryption
2. DES result → Vigenere Decryption
3. Vigenere result → Caesar Decryption → Plaintext
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.caesar_cipher import caesar_encrypt, caesar_decrypt
from utils.vigenere_cipher import vigenere_encrypt, vigenere_decrypt
from utils.des_encryption import DESEncryption


class SuperEncrypt:
    """
    Super Encryption - Triple layer security
    """
    
    def __init__(self, caesar_shift=3, vigenere_key="KEY", des_key="secret12"):
        """
        Initialize Super Encrypt dengan 3 kunci
        
        Args:
            caesar_shift (int): Shift untuk Caesar Cipher (1-25)
            vigenere_key (str): Keyword untuk Vigenere Cipher
            des_key (str): Key untuk DES (8 characters)
        """
        self.caesar_shift = caesar_shift
        self.vigenere_key = vigenere_key
        
        # Ensure DES key is exactly 8 bytes
        if len(des_key) < 8:
            des_key = des_key.ljust(8, '0')  # Pad dengan '0'
        elif len(des_key) > 8:
            des_key = des_key[:8]  # Truncate ke 8 chars
        
        self.des_key = des_key
        self.des_cipher = DESEncryption(des_key)
    
    def encrypt(self, plaintext):
        """
        Encrypt text dengan 3 layer: Caesar → Vigenere → DES
        
        Args:
            plaintext (str): Text to encrypt
            
        Returns:
            dict: Triple-encrypted result dengan ciphertext dan IV
        """
        # Layer 1: Caesar Cipher
        caesar_result = caesar_encrypt(plaintext, self.caesar_shift)
        print(f"  Layer 1 (Caesar)   : {caesar_result}")
        
        # Layer 2: Vigenere Cipher
        vigenere_result = vigenere_encrypt(caesar_result, self.vigenere_key)
        print(f"  Layer 2 (Vigenere) : {vigenere_result}")
        
        # Layer 3: DES Encryption
        des_result = self.des_cipher.encrypt(vigenere_result)
        print(f"  Layer 3 (DES)      : {des_result['ciphertext'][:20]}...")
        
        # Return only ciphertext and iv (not key for security)
        return {
            'ciphertext': des_result['ciphertext'],
            'iv': des_result['iv']
        }
    
    def decrypt(self, encrypted_data):
        """
        Decrypt text dengan reverse order: DES → Vigenere → Caesar
        
        Args:
            encrypted_data (dict): Dict with 'ciphertext' and 'iv' keys
            
        Returns:
            str: Original plaintext
        """
        # Extract ciphertext and IV
        ciphertext = encrypted_data['ciphertext']
        iv = encrypted_data['iv']
        
        # Layer 3 (reverse): DES Decryption
        des_result = self.des_cipher.decrypt(ciphertext, iv)
        print(f"  Layer 3 (DES)      : {des_result}")
        
        # Layer 2 (reverse): Vigenere Decryption
        vigenere_result = vigenere_decrypt(des_result, self.vigenere_key)
        print(f"  Layer 2 (Vigenere) : {vigenere_result}")
        
        # Layer 1 (reverse): Caesar Decryption
        caesar_result = caesar_decrypt(vigenere_result, self.caesar_shift)
        print(f"  Layer 1 (Caesar)   : {caesar_result}")
        
        return caesar_result


# Helper functions untuk usage mudah
def super_encrypt(text, caesar_shift=3, vigenere_key="KEY", des_key="secret12"):
    """
    Encrypt text dengan Super Encrypt
    
    Args:
        text (str): Text to encrypt
        caesar_shift (int): Shift untuk Caesar
        vigenere_key (str): Key untuk Vigenere
        des_key (str): Key untuk DES (8 chars)
    
    Returns:
        dict: {'ciphertext': str, 'iv': str}
    """
    cipher = SuperEncrypt(caesar_shift, vigenere_key, des_key)
    return cipher.encrypt(text)


def super_decrypt(encrypted_data, caesar_shift=3, vigenere_key="KEY", des_key="secret12"):
    """
    Decrypt text dengan Super Encrypt
    
    Args:
        encrypted_data (dict): Dict with 'ciphertext' and 'iv'
        caesar_shift (int): Shift untuk Caesar
        vigenere_key (str): Key untuk Vigenere
        des_key (str): Key untuk DES (8 chars)
    
    Returns:
        str: Original plaintext
    """
    cipher = SuperEncrypt(caesar_shift, vigenere_key, des_key)
    return cipher.decrypt(encrypted_data)


# Testing
if __name__ == "__main__":
    print("="*60)
    print("SUPER ENCRYPT - Triple Layer Encryption Testing")
    print("="*60)
    
    # Test 1: Basic encryption with default keys
    print("\n1. Basic Encryption (Default Keys):")
    print("-" * 60)
    plaintext = "Hello World!"
    
    cipher = SuperEncrypt()
    print(f"Original Text: {plaintext}")
    print(f"\nEncryption Process:")
    encrypted = cipher.encrypt(plaintext)
    
    print(f"\nDecryption Process:")
    decrypted = cipher.decrypt(encrypted)
    
    print(f"\nFinal Result:")
    print(f"  Plaintext  : {plaintext}")
    print(f"  Encrypted  : {encrypted}")
    print(f"  Decrypted  : {decrypted}")
    print(f"  ✓ Match    : {plaintext == decrypted}")
    
    # Test 2: Custom keys
    print("\n\n2. Custom Keys:")
    print("-" * 60)
    plaintext = "Secret Message 123"
    caesar_shift = 7
    vigenere_key = "CRYPTO"
    des_key = "mykey789"
    
    cipher = SuperEncrypt(caesar_shift, vigenere_key, des_key)
    print(f"Original Text  : {plaintext}")
    print(f"Caesar Shift   : {caesar_shift}")
    print(f"Vigenere Key   : {vigenere_key}")
    print(f"DES Key        : {des_key}")
    
    print(f"\nEncryption Process:")
    encrypted = cipher.encrypt(plaintext)
    
    print(f"\nDecryption Process:")
    decrypted = cipher.decrypt(encrypted)
    
    print(f"\nFinal Result:")
    print(f"  ✓ Match    : {plaintext == decrypted}")
    
    # Test 3: Long text
    print("\n\n3. Long Text:")
    print("-" * 60)
    plaintext = "The quick brown fox jumps over the lazy dog"
    
    cipher = SuperEncrypt(5, "SECRET", "pass1234")
    print(f"Original: {plaintext}")
    
    print(f"\nEncryption Process:")
    encrypted = cipher.encrypt(plaintext)
    
    print(f"\nDecryption Process:")
    decrypted = cipher.decrypt(encrypted)
    
    print(f"\nFinal: {decrypted}")
    print(f"✓ Match: {plaintext == decrypted}")
    
    # Test 4: Helper functions
    print("\n\n4. Helper Functions:")
    print("-" * 60)
    text = "Test Helper Functions"
    
    encrypted = super_encrypt(text, 13, "PASS", "testkey1")
    print(f"Encrypted: {encrypted}")
    
    decrypted = super_decrypt(encrypted, 13, "PASS", "testkey1")
    print(f"Decrypted: {decrypted}")
    print(f"✓ Match: {text == decrypted}")
    
    # Test 5: Special characters
    print("\n\n5. Special Characters & Numbers:")
    print("-" * 60)
    plaintext = "Test @#$% 12345 ABC xyz!"
    
    cipher = SuperEncrypt(3, "KEY", "secret12")
    print(f"Original: {plaintext}")
    
    print(f"\nEncryption:")
    encrypted = cipher.encrypt(plaintext)
    
    print(f"\nDecryption:")
    decrypted = cipher.decrypt(encrypted)
    
    print(f"\n✓ Match: {plaintext == decrypted}")
    
    print("\n" + "="*60)
    print("✅ All Super Encrypt tests completed!")
    print("="*60)
