"""
Configuration Module
Modul untuk membaca environment variables dari file .env
"""

import os
from pathlib import Path


class Config:
    """Class untuk mengelola konfigurasi aplikasi."""
    
    def __init__(self, env_file=".env"):
        """
        Inisialisasi Config dan load environment variables.
        
        Args:
            env_file: Path ke file .env (default: ".env")
        """
        self.env_file = env_file
        self.env_vars = {}
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables dari file .env"""
        # Try multiple locations untuk .env file
        current_dir = Path(__file__).parent
        
        # Possible locations (in order of priority)
        possible_paths = [
            current_dir / self.env_file,              # python/.env
            current_dir.parent / self.env_file,       # project_root/.env
            Path.cwd() / self.env_file,               # current working directory/.env
            Path(os.getcwd()) / self.env_file,        # alternative cwd/.env
        ]
        
        env_path = None
        for path in possible_paths:
            if path.exists():
                env_path = path
                print(f"✓ File .env found at: {path}")
                break
        
        if not env_path:
            print(f"⚠ File {self.env_file} tidak ditemukan di:")
            for path in possible_paths:
                print(f"   - {path}")
            print("⚠ Menggunakan default values atau OS environment variables")
            return
        
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip komentar dan baris kosong
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Hapus quotes jika ada
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        self.env_vars[key] = value
                        os.environ[key] = value
            
            print(f"✓ File {self.env_file} berhasil dimuat ({len(self.env_vars)} variables)")
        
        except Exception as e:
            print(f"✗ Error membaca {self.env_file}: {e}")
    
    def get(self, key, default=None):
        """Dapatkan nilai environment variable."""
        return self.env_vars.get(key) or os.environ.get(key) or default
    
    def get_int(self, key, default=0):
        """Dapatkan nilai sebagai integer."""
        value = self.get(key)
        try:
            return int(value) if value else default
        except ValueError:
            return default
    
    def get_bool(self, key, default=False):
        """Dapatkan nilai sebagai boolean."""
        value = self.get(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    # Database Configuration
    @property
    def db_host(self):
        return self.get('DB_HOST', 'localhost')
    
    @property
    def db_user(self):
        return self.get('DB_USER', 'root')
    
    @property
    def db_password(self):
        return self.get('DB_PASSWORD', '')
    
    @property
    def db_database(self):
        return self.get('DB_DATABASE', 'test')
    
    @property
    def db_port(self):
        return self.get_int('DB_PORT', 3306)
    
    # Flask Configuration
    @property
    def flask_host(self):
        return '0.0.0.0'
    
    @property
    def flask_port(self):
        return 5000
    
    @property
    def flask_debug(self):
        return True
    
    @property
    def secret_key(self):
        return self.get('SECRET_KEY', 'dev-secret-key-change-this')
    
    def get_db_config(self):
        """Dapatkan konfigurasi database sebagai dictionary."""
        return {
            'host': self.db_host,
            'user': self.db_user,
            'password': self.db_password,
            'database': self.db_database,
            'port': self.db_port
        }
    
    def display_config(self):
        """Tampilkan konfigurasi untuk debugging."""
        print("\n" + "="*50)
        print("⚙ CONFIGURATION")
        print("="*50)
        print(f"Database Host  : {self.db_host}:{self.db_port}")
        print(f"Database User  : {self.db_user}")
        print(f"Database Name  : {self.db_database}")
        print(f"Flask Host     : {self.flask_host}:{self.flask_port}")
        print(f"Flask Debug    : {self.flask_debug}")
        print("="*50 + "\n")


# Singleton instance
config = Config()


if __name__ == "__main__":
    cfg = Config()
    cfg.display_config()
    
    print("Database Config:")
    print(cfg.get_db_config())
