"""
AES File Encryption Module
Modul untuk enkripsi dan dekripsi file menggunakan algoritma AES (Advanced Encryption Standard)
AES lebih aman dan lebih cepat dari DES/Blowfish
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os


class AESFileEncryption:
    """Class untuk enkripsi dan dekripsi file dengan AES."""
    
    def __init__(self, key=None):
        """
        Inisialisasi AES dengan key.
        
        Args:
            key: Key 16/24/32 bytes (128/192/256 bit). Jika None, generate random.
        
        Note:
            AES mendukung key size: 16 bytes (AES-128), 24 bytes (AES-192), 32 bytes (AES-256)
        """
        if key is None:
            # Generate random 32-byte key (AES-256)
            self.key = get_random_bytes(32)
        elif isinstance(key, str):
            # Convert string ke bytes, pastikan 32 bytes
            key_bytes = key.encode('utf-8')
            if len(key_bytes) < 32:
                # Pad dengan nul bytes jika kurang
                self.key = key_bytes.ljust(32, b'\0')
            elif len(key_bytes) > 32:
                # Truncate jika lebih
                self.key = key_bytes[:32]
            else:
                self.key = key_bytes
        elif isinstance(key, bytes):
            if len(key) not in [16, 24, 32]:
                raise ValueError("AES key must be 16, 24, or 32 bytes!")
            self.key = key
        else:
            raise TypeError("Key must be string or bytes!")
    
    def encrypt_file(self, input_file, output_file=None):
        """
        Enkripsi file.
        
        Args:
            input_file: Path file yang akan dienkripsi
            output_file: Path file hasil enkripsi (optional, default: input_file.enc)
        
        Returns:
            Dictionary dengan info enkripsi
        
        Example:
            >>> aes = AESFileEncryption("mypassword123")
            >>> result = aes.encrypt_file("dokumen.pdf")
            >>> print(result['encrypted_file'])
            'dokumen.pdf.enc'
        """
        if output_file is None:
            output_file = input_file + ".enc"
        
        # Baca file
        with open(input_file, 'rb') as f:
            data = f.read()
        
        # Create AES cipher
        cipher = AES.new(self.key, AES.MODE_CBC)
        
        # Encrypt
        ciphertext = cipher.encrypt(pad(data, AES.block_size))
        
        # Simpan: IV (16 bytes) + ciphertext
        with open(output_file, 'wb') as f:
            f.write(cipher.iv)  # Save IV di awal file
            f.write(ciphertext)
        
        return {
            'success': True,
            'original_file': input_file,
            'encrypted_file': output_file,
            'original_size': len(data),
            'encrypted_size': len(ciphertext) + 16,  # +16 untuk IV
            'algorithm': 'AES-256-CBC'
        }
    
    def decrypt_file(self, input_file, output_file=None):
        """
        Dekripsi file.
        
        Args:
            input_file: Path file terenkripsi
            output_file: Path file hasil dekripsi (optional, default: hapus .enc)
        
        Returns:
            Dictionary dengan info dekripsi
        
        Example:
            >>> aes = AESFileEncryption("mypassword123")
            >>> result = aes.decrypt_file("dokumen.pdf.enc")
            >>> print(result['decrypted_file'])
            'dokumen.pdf'
        """
        if output_file is None:
            # Hapus extension .enc
            if input_file.endswith('.enc'):
                output_file = input_file[:-4]
            else:
                output_file = input_file + ".dec"
        
        # Baca file terenkripsi
        with open(input_file, 'rb') as f:
            iv = f.read(16)  # Baca IV (16 bytes pertama)
            ciphertext = f.read()  # Sisanya adalah ciphertext
        
        # Create AES cipher dengan IV yang sama
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # Decrypt
        data = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        # Simpan file hasil dekripsi
        with open(output_file, 'wb') as f:
            f.write(data)
        
        return {
            'success': True,
            'encrypted_file': input_file,
            'decrypted_file': output_file,
            'decrypted_size': len(data),
            'algorithm': 'AES-256-CBC'
        }
    
    def get_key_hex(self):
        """Get key dalam format hexadecimal."""
        return self.key.hex()


# Helper functions

def encrypt_file(input_file, password, output_file=None):
    """
    Enkripsi file dengan password (helper function).
    
    Args:
        input_file: File yang akan dienkripsi
        password: Password (string)
        output_file: File output (optional)
    
    Returns:
        Info enkripsi
    """
    aes = AESFileEncryption(password)
    return aes.encrypt_file(input_file, output_file)


def decrypt_file(input_file, password, output_file=None):
    """
    Dekripsi file dengan password (helper function).
    
    Args:
        input_file: File terenkripsi
        password: Password (string)
        output_file: File output (optional)
    
    Returns:
        Info dekripsi
    """
    aes = AESFileEncryption(password)
    return aes.decrypt_file(input_file, output_file)
