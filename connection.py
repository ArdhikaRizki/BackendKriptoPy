"""
Database Connection Module
Modul untuk mengelola koneksi database MySQL
"""

import mysql.connector
from mysql.connector import Error


class DatabaseConnection:
    """Class untuk mengelola koneksi database MySQL."""
    
    def __init__(self, host="localhost", user="root", password="", database="test", port=3306):
        """
        Inisialisasi koneksi database.
        
        Args:
            host: Host database (default: localhost)
            user: Username database (default: root)
            password: Password database (default: '')
            database: Nama database (default: test)
            port: Port database (default: 3306)
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
    
    def connect(self):
        """Membuat koneksi ke database MySQL."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=True,  # ← AUTO COMMIT setiap query!
                pool_name="mypool",
                pool_size=5
            )
            if self.connection.is_connected():
                print(f"✓ Koneksi ke MySQL database '{self.database}' berhasil")
                return self.connection
        except Error as e:
            print(f"✗ Error koneksi database: {e}")
            return None
    
    def disconnect(self):
        """Menutup koneksi database."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Koneksi database ditutup")
    
    def get_connection(self):
        """Mendapatkan koneksi database."""
        if not self.connection or not self.connection.is_connected():
            return self.connect()
        return self.connection
    
    def execute_query(self, query, params=None):
        """
        Menjalankan query (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query string
            params: Parameter untuk query (opsional)
            
        Returns:
            True jika berhasil, False jika gagal
        """
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            connection.commit()
            print("✓ Query berhasil dijalankan")
            return True
            
        except Error as e:
            print(f"✗ Error execute query: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    
    def execute_read_query(self, query, params=None):
        """
        Menjalankan query SELECT dan mengembalikan hasil.
        
        Args:
            query: SQL query string
            params: Parameter untuk query (opsional)
            
        Returns:
            List of tuples atau None jika error
        """
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchall()
            return result
            
        except Error as e:
            print(f"✗ Error read query: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def execute_read_one(self, query, params=None):
        """
        Menjalankan query SELECT dan mengembalikan satu hasil.
        
        Args:
            query: SQL query string
            params: Parameter untuk query (opsional)
            
        Returns:
            Single tuple atau None
        """
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchone()
            return result
            
        except Error as e:
            print(f"✗ Error read one: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def execute_read_dict(self, query, params=None):
        """
        Menjalankan query SELECT dan mengembalikan hasil sebagai dictionary.
        
        Args:
            query: SQL query string
            params: Parameter untuk query (opsional)
            
        Returns:
            List of dictionaries
        """
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchall()
            return result
            
        except Error as e:
            print(f"✗ Error read dict: {e}")
            return None
        finally:
            if cursor:
                cursor.close()


# Helper function untuk koneksi cepat
def get_db_connection(host="localhost", user="root", password="", database="test", port=3306):
    """
    Helper function untuk mendapatkan koneksi database.
    
    Returns:
        DatabaseConnection object
    """
    db = DatabaseConnection(host, user, password, database, port)
    db.connect()
    return db


# Test connection
if __name__ == "__main__":
    print("=== Test Database Connection ===\n")
    
    # Buat koneksi
    db = get_db_connection(
        host="localhost",
        user="root",
        password="",
        database="test",
        port=3306
    )
    
    if db.connection:
        # Test read query
        print("\nTest read query:")
        results = db.execute_read_query("SELECT * FROM users LIMIT 5")
        if results:
            print(f"Ditemukan {len(results)} records:")
            for row in results:
                print(f"  {row}")
        
        # Test read as dictionary
        print("\nTest read as dictionary:")
        results_dict = db.execute_read_dict("SELECT * FROM users LIMIT 3")
        if results_dict:
            for row in results_dict:
                print(f"  {row}")
        
        # Tutup koneksi
        db.disconnect()
