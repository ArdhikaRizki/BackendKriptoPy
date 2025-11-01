"""
Steganography Module - LSB (Least Significant Bit) Implementation
Menyembunyikan dan mengekstrak pesan rahasia dalam gambar
"""

from PIL import Image
import io
import base64


class Steganography:
    """
    Class untuk encode dan decode pesan rahasia dalam gambar menggunakan LSB
    """
    
    def __init__(self):
        self.delimiter = "###END###"  # Penanda akhir pesan
    
    def encode_message(self, image_base64, secret_message):
        """
        Menyembunyikan pesan rahasia dalam gambar
        
        Args:
            image_base64 (str): Gambar dalam format base64
            secret_message (str): Pesan yang akan disembunyikan
            
        Returns:
            str: Gambar yang sudah berisi pesan rahasia dalam format base64
        """
        try:
            # Decode base64 ke bytes
            image_bytes = base64.b64decode(image_base64)
            
            # Buka gambar dari bytes
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert ke RGB jika belum
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Tambahkan delimiter di akhir pesan
            message_with_delimiter = secret_message + self.delimiter
            
            # Convert pesan ke binary
            binary_message = ''.join(format(ord(char), '08b') for char in message_with_delimiter)
            
            # Cek apakah gambar cukup besar untuk menampung pesan
            max_bytes = img.width * img.height * 3  # RGB = 3 bytes per pixel
            if len(binary_message) > max_bytes:
                raise ValueError(f"Pesan terlalu panjang! Maksimal {max_bytes // 8} karakter, tapi pesan {len(binary_message) // 8} karakter")
            
            # Load pixel data
            pixels = list(img.getdata())
            new_pixels = []
            
            binary_index = 0
            
            for pixel in pixels:
                # Pixel RGB tuple (r, g, b)
                r, g, b = pixel
                
                # Modify LSB dari setiap komponen RGB
                if binary_index < len(binary_message):
                    r = self._modify_lsb(r, binary_message[binary_index])
                    binary_index += 1
                
                if binary_index < len(binary_message):
                    g = self._modify_lsb(g, binary_message[binary_index])
                    binary_index += 1
                
                if binary_index < len(binary_message):
                    b = self._modify_lsb(b, binary_message[binary_index])
                    binary_index += 1
                
                new_pixels.append((r, g, b))
                
                # Jika sudah selesai encode semua bit, break
                if binary_index >= len(binary_message):
                    # Tambahkan sisa pixel yang tidak dimodifikasi
                    new_pixels.extend(pixels[len(new_pixels):])
                    break
            
            # Buat gambar baru dengan pixel yang sudah dimodifikasi
            encoded_img = Image.new(img.mode, img.size)
            encoded_img.putdata(new_pixels)
            
            # Convert kembali ke base64
            buffered = io.BytesIO()
            encoded_img.save(buffered, format="PNG")  # Gunakan PNG untuk lossless
            encoded_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return encoded_base64
            
        except Exception as e:
            raise Exception(f"Error encoding message: {str(e)}")
    
    def decode_message(self, image_base64):
        """
        Mengekstrak pesan rahasia dari gambar
        
        Args:
            image_base64 (str): Gambar yang berisi pesan rahasia dalam format base64
            
        Returns:
            str: Pesan rahasia yang tersembunyi
        """
        try:
            # Decode base64 ke bytes
            image_bytes = base64.b64decode(image_base64)
            
            # Buka gambar dari bytes
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert ke RGB jika belum
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Load pixel data
            pixels = list(img.getdata())
            
            # Extract binary message dari LSB
            binary_message = ""
            
            for pixel in pixels:
                r, g, b = pixel
                
                # Extract LSB dari setiap komponen RGB
                binary_message += str(r & 1)
                binary_message += str(g & 1)
                binary_message += str(b & 1)
            
            # Convert binary ke text
            message = ""
            char_count = 0
            max_chars = 10000  # Limit untuk mencegah infinite loop
            
            for i in range(0, len(binary_message), 8):
                byte = binary_message[i:i+8]
                if len(byte) == 8:
                    try:
                        char = chr(int(byte, 2))
                        message += char
                        char_count += 1
                        
                        # Cek apakah sudah mencapai delimiter
                        if message.endswith(self.delimiter):
                            # Hapus delimiter dari pesan
                            message = message[:-len(self.delimiter)]
                            return message
                        
                        # Safety limit
                        if char_count > max_chars:
                            break
                    except ValueError:
                        # Invalid character, skip
                        continue
            
            # Jika sampai sini berarti tidak ketemu delimiter
            # Kemungkinan gambar tidak ada pesan steganografi
            raise Exception("Delimiter tidak ditemukan. Gambar ini mungkin tidak mengandung pesan steganografi atau pesan telah rusak.")
            
        except Exception as e:
            if "Delimiter tidak ditemukan" in str(e):
                raise e
            raise Exception(f"Error decoding message: {str(e)}")
    
    def _modify_lsb(self, value, bit):
        """
        Modify Least Significant Bit dari sebuah nilai
        
        Args:
            value (int): Nilai RGB (0-255)
            bit (str): Bit '0' atau '1'
            
        Returns:
            int: Nilai yang sudah dimodifikasi LSB-nya
        """
        # Clear LSB (set ke 0)
        value = value & 0xFE
        
        # Set LSB sesuai bit yang diinginkan
        if bit == '1':
            value = value | 1
        
        return value
    
    def check_capacity(self, image_base64):
        """
        Cek kapasitas maksimal pesan yang bisa disimpan dalam gambar
        
        Args:
            image_base64 (str): Gambar dalam format base64
            
        Returns:
            dict: Informasi kapasitas gambar
        """
        try:
            # Decode base64 ke bytes
            image_bytes = base64.b64decode(image_base64)
            
            # Buka gambar dari bytes
            img = Image.open(io.BytesIO(image_bytes))
            
            # Hitung kapasitas
            total_pixels = img.width * img.height
            max_bits = total_pixels * 3  # RGB = 3 bits per pixel (LSB dari R, G, B)
            max_chars = max_bits // 8  # 8 bits = 1 character
            
            # Kurangi dengan delimiter
            usable_chars = max_chars - len(self.delimiter)
            
            return {
                'width': img.width,
                'height': img.height,
                'total_pixels': total_pixels,
                'max_bits': max_bits,
                'max_characters': usable_chars,
                'max_characters_with_delimiter': max_chars
            }
            
        except Exception as e:
            raise Exception(f"Error checking capacity: {str(e)}")


# Fungsi helper untuk penggunaan langsung
def hide_message(image_base64, message):
    """
    Fungsi helper untuk menyembunyikan pesan dalam gambar
    
    Args:
        image_base64 (str): Gambar dalam format base64
        message (str): Pesan yang akan disembunyikan
        
    Returns:
        str: Gambar yang sudah berisi pesan dalam format base64
    """
    stego = Steganography()
    return stego.encode_message(image_base64, message)


def extract_message(image_base64):
    """
    Fungsi helper untuk mengekstrak pesan dari gambar
    
    Args:
        image_base64 (str): Gambar yang berisi pesan dalam format base64
        
    Returns:
        str: Pesan yang tersembunyi
    """
    stego = Steganography()
    return stego.decode_message(image_base64)


def get_image_capacity(image_base64):
    """
    Fungsi helper untuk cek kapasitas gambar
    
    Args:
        image_base64 (str): Gambar dalam format base64
        
    Returns:
        dict: Informasi kapasitas
    """
    stego = Steganography()
    return stego.check_capacity(image_base64)
