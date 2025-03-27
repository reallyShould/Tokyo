import sqlite3
import bcrypt
import config
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password_hash, role):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
    
    def get_id(self):
        return str(self.id)

    def is_specialist(self):
        return self.role == 'system-adm' or self.role == 'admin'

class Users:
    def init_db(self):
        conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                fullname TEXT,
                mail TEXT,
                spec TEXT,
                password_hash BLOB NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'open',
                resolution TEXT,  -- Поле для описания решения
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def register_user(self, username, password, role='user'):
        try:
            conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()

            password_hash = self.hash_password(password)
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                         (username, password_hash, role))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
        except Exception as e:
            conn.close()
            raise e

    def checkUser(self, username):
        conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is None

    def login_user(self, username, password):
        conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result is None:
            return False
        
        stored_hash = result[2]
        
        try:
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return User(result[0], result[1], result[2], result[3])
            return False
        except Exception:
            return False

    def get_user(self, username):
        conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return User(result[0], result[1], result[2], result[3])
        return None

    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return User(result[0], result[1], result[2], result[3])
        return None

    def get_username_by_id(self, user_id):
        conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return "Неизвестный пользователь"