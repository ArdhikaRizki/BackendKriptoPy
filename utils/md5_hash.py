"""
MD5 Hashing Module
Modul untuk hashing password menggunakan algoritma MD5
"""

import hashlib


def hash_password_md5(password):
    """
    Hash password menggunakan MD5.
    
    Args:
        password: Password plaintext (string)
    
    Returns:
        Hashed password dalam format hexadecimal
    
    Example:
        >>> hash_password_md5("password123")
        '482c811da5d5b4bc6d497ffa98491e38'
    """
    # Konversi password ke bytes
    password_bytes = password.encode('utf-8')

    # Hash dengan MD5
    md5_hash = hashlib.md5(password_bytes)

    # Return dalam format hexadecimal
    return md5_hash.hexdigest()


def verify_password_md5(password, hashed_password):
    """
    Verifikasi password dengan hash MD5.
    
    Args:
        password: Password plaintext yang diinput user
        hashed_password: Hash MD5 yang tersimpan di database
    
    Returns:
        True jika cocok, False jika tidak
    
    Example:
        >>> hashed = hash_password_md5("password123")
        >>> verify_password_md5("password123", hashed)
        True
        >>> verify_password_md5("wrongpass", hashed)
        False
    """
    # Hash password yang diinput
    password_hash = hash_password_md5(password)

    # Bandingkan dengan hash dari database
    return password_hash == hashed_password

