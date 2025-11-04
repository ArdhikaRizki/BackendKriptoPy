"""
Database Connection Module
Modul untuk mengelola koneksi database MySQL
"""

import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool


class DatabaseConnection:
    """Class untuk mengelola koneksi database MySQL."""
    
    def __init__(self, host="localhost", user="root", password="", database="test", port=3306):
        """
        Inisialisasi koneksi database dengan CONNECTION POOL.
        
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
        self.pool = None  # Connection pool
    
    def connect(self):
        """Membuat CONNECTION POOL ke database MySQL (bukan single connection)."""
        try:
            # Create connection pool with 5-10 connections
            self.pool = MySQLConnectionPool(
                pool_name="kripto_pool",
                pool_size=10,  # Max 10 concurrent connections
                pool_reset_session=True,  # Reset session setiap ambil connection
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=True  # AUTO COMMIT setiap query
            )
            
            print(f"✓ Connection Pool ke MySQL database '{self.database}' berhasil (pool_size=10)")
            return self.pool
        except Error as e:
            print(f"✗ Error koneksi database: {e}")
            return None
    
    def disconnect(self):
        """Menutup koneksi database."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Koneksi database ditutup")
    
    def get_connection(self):
        """Mendapatkan koneksi dari pool (bukan shared connection)."""
        if not self.pool:
            self.connect()
        
        # Get connection dari pool (ini auto-managed, thread-safe)
        return self.pool.get_connection()
    
    def execute_query(self, query, params=None):
        """
        Menjalankan query (INSERT, UPDATE, DELETE).
        Ambil connection dari POOL → execute → return to pool.
        
        Args:
            query: SQL query string
            params: Parameter untuk query (opsional)
            
        Returns:
            True jika berhasil, False jika gagal
        """
        cursor = None
        connection = None
        try:
            # Get connection from POOL (bukan buat baru!)
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Autocommit already enabled in pool config
            connection.commit()
            print("✓ Query berhasil dijalankan")
            return True
            
        except Error as e:
            print(f"✗ Error execute query: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()  # Return connection to POOL (bukan destroy!)
    
    def execute_read_query(self, query, params=None):
        """
        Menjalankan query SELECT dan mengembalikan hasil.
        Ambil connection dari POOL → execute → return to pool.
        
        Args:
            query: SQL query string
            params: Parameter untuk query (opsional)
            
        Returns:
            List of tuples atau None jika error
        """
        cursor = None
        connection = None
        try:
            # Get connection from POOL (bukan buat baru!)
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
            if connection and connection.is_connected():
                connection.close()  # Return connection to POOL
    
    def execute_read_one(self, query, params=None):
        """
        Menjalankan query SELECT dan mengembalikan satu hasil.
        Ambil connection dari POOL → execute → return to pool.
        
        Args:
            query: SQL query string
            params: Parameter untuk query (opsional)
            
        Returns:
            Single tuple atau None
        """
        cursor = None
        connection = None
        try:
            # Get connection from POOL (bukan buat baru!)
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
            if connection and connection.is_connected():
                connection.close()  # Return connection to POOL
    
    def execute_read_dict(self, query, params=None):
        """
        Menjalankan query SELECT dan mengembalikan hasil sebagai dictionary.
        Ambil connection dari POOL → execute → return to pool.
        
        Args:
            query: SQL query string
            params: Parameter untuk query (opsional)
            
        Returns:
            List of dictionaries
        """
        cursor = None
        connection = None
        try:
            # Get connection from POOL (bukan buat baru!)
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
            if connection and connection.is_connected():
                connection.close()  # Return connection to POOL

    def execute_insert(self, query, params=None):
        """
        🆕 Menjalankan INSERT query dan return last insert ID.
        Khusus untuk INSERT yang butuh AUTO_INCREMENT ID.
        
        Args:
            query: SQL INSERT query string
            params: Parameter untuk query (opsional)
            
        Returns:
            last_insert_id (int) jika berhasil, None jika gagal
        """
        cursor = None
        connection = None
        try:
            # Get connection from POOL
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Commit
            connection.commit()
            
            # Get last insert ID dari cursor (PENTING: dari cursor yang sama!)
            last_id = cursor.lastrowid
            
            print(f"✓ INSERT berhasil: last_insert_id={last_id}")
            return last_id
            
        except Error as e:
            print(f"✗ Error execute INSERT: {e}")
            if connection:
                connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()  # Return connection to POOL


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
