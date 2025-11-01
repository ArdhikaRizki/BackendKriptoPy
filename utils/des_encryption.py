"""
DES Encryption Module
Modul untuk enkripsi dan dekripsi menggunakan algoritma DES (Data Encryption Standard)
Menggunakan library pycryptodome
"""

from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64


class DESEncryption:
    """Class untuk enkripsi dan dekripsi DES."""
    
    def __init__(self, key=None):
        """
        Inisialisasi DES dengan key.
        
        Args:
            key: Key 8 bytes (64 bit). Jika None, akan generate random key.
        
        Note:
            DES menggunakan key 8 bytes (64 bit)
            Key harus PERSIS 8 bytes!
        """
        if key is None:
            # Generate random 8-byte key
            self.key = get_random_bytes(8)
        elif isinstance(key, str):
            # Jika key string, convert ke bytes dan pastikan 8 bytes
            key_bytes = key.encode('utf-8')
            if len(key_bytes) < 8:
                # Pad dengan spasi jika kurang dari 8 bytes
                self.key = key_bytes.ljust(8, b' ')
            elif len(key_bytes) > 8:
                # Truncate jika lebih dari 8 bytes
                self.key = key_bytes[:8]
            else:
                self.key = key_bytes
        elif isinstance(key, bytes):
            if len(key) != 8:
                raise ValueError("DES key must be exactly 8 bytes!")
            self.key = key
        else:
            raise TypeError("Key must be string or bytes!")
    
    def encrypt(self, plaintext):
        """
        Enkripsi plaintext menggunakan DES.
        
        Args:
            plaintext: Text yang akan dienkripsi (string)
        
        Returns:
            Dictionary dengan ciphertext (base64) dan IV (base64)
        
        Example:
            >>> des = DESEncryption("mykey123")
            >>> result = des.encrypt("Hello World")
            >>> print(result['ciphertext'])
            'xK7jF3mP...'
        """
        # Convert plaintext ke bytes
        if isinstance(plaintext, str):
            plaintext_bytes = plaintext.encode('utf-8')
        else:
            plaintext_bytes = plaintext
        
        # Create DES cipher dengan mode CBC (Cipher Block Chaining)
        # Mode CBC lebih aman dari ECB
        cipher = DES.new(self.key, DES.MODE_CBC)
        
        # Pad plaintext agar kelipatan 8 bytes (DES block size = 8 bytes)
        padded_plaintext = pad(plaintext_bytes, DES.block_size)
        
        # Encrypt
        ciphertext = cipher.encrypt(padded_plaintext)
        
        # Return ciphertext dan IV dalam base64
        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'iv': base64.b64encode(cipher.iv).decode('utf-8'),
            'key': base64.b64encode(self.key).decode('utf-8')
        }
    
    def decrypt(self, ciphertext_b64, iv_b64):
        """
        Dekripsi ciphertext menggunakan DES.
        
        Args:
            ciphertext_b64: Ciphertext dalam format base64 (string)
            iv_b64: Initialization Vector dalam format base64 (string)
        
        Returns:
            Plaintext (string)
        
        Example:
            >>> des = DESEncryption("mykey123")
            >>> plaintext = des.decrypt(ciphertext, iv)
            >>> print(plaintext)
            'Hello World'
        """
        # Decode base64
        ciphertext = base64.b64decode(ciphertext_b64)
        iv = base64.b64decode(iv_b64)
        
        # Create DES cipher dengan IV yang sama
        cipher = DES.new(self.key, DES.MODE_CBC, iv)
        
        # Decrypt
        padded_plaintext = cipher.decrypt(ciphertext)
        
        # Remove padding
        plaintext_bytes = unpad(padded_plaintext, DES.block_size)
        
        # Convert ke string
        return plaintext_bytes.decode('utf-8')
    
    def encrypt_to_hex(self, plaintext):
        """
        Enkripsi plaintext dan return dalam format hexadecimal.
        
        Args:
            plaintext: Text yang akan dienkripsi
        
        Returns:
            Dictionary dengan ciphertext (hex) dan IV (hex)
        """
        result = self.encrypt(plaintext)
        
        return {
            'ciphertext': base64.b64decode(result['ciphertext']).hex(),
            'iv': base64.b64decode(result['iv']).hex(),
            'key': base64.b64decode(result['key']).hex()
        }
    
    def decrypt_from_hex(self, ciphertext_hex, iv_hex):
        """
        Dekripsi ciphertext dari format hexadecimal.
        
        Args:
            ciphertext_hex: Ciphertext dalam format hex
            iv_hex: IV dalam format hex
        
        Returns:
            Plaintext (string)
        """
        # Convert hex ke bytes lalu ke base64
        ciphertext_b64 = base64.b64encode(bytes.fromhex(ciphertext_hex)).decode('utf-8')
        iv_b64 = base64.b64encode(bytes.fromhex(iv_hex)).decode('utf-8')
        
        return self.decrypt(ciphertext_b64, iv_b64)
    
    def get_key_base64(self):
        """
        Get key dalam format base64.
        
        Returns:
            Key (base64 string)
        """
        return base64.b64encode(self.key).decode('utf-8')
    
    def get_key_hex(self):
        """
        Get key dalam format hexadecimal.
        
        Returns:
            Key (hex string)
        """
        return self.key.hex()


# Helper functions untuk penggunaan praktis

def encrypt_text(plaintext, key):
    """
    Enkripsi text dengan DES (helper function).
    
    Args:
        plaintext: Text yang akan dienkripsi
        key: Key (string, 8 karakter)
    
    Returns:
        Dictionary dengan ciphertext, iv, dan key
    """
    des = DESEncryption(key)
    return des.encrypt(plaintext)


def decrypt_text(ciphertext_b64, iv_b64, key):
    """
    Dekripsi text dengan DES (helper function).
    
    Args:
        ciphertext_b64: Ciphertext (base64)
        iv_b64: IV (base64)
        key: Key (string, 8 karakter)
    
    Returns:
        Plaintext (string)
    """
    des = DESEncryption(key)
    return des.decrypt(ciphertext_b64, iv_b64)

