import sqlite3
import bcrypt
import config

class Users:

    def init_db(self):
        conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    def register_user(self, username, password):
        conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()

        password_hash = self.hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                    (username, password_hash))
        conn.commit()
        conn.close()
        return True

    def checkUser(self, username):
        conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False
        else:
            return True
