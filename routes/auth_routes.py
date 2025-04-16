from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, login_required, logout_user
from models import Users
import sqlite3
import config

users = Users()
auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route("/", methods=['GET', 'POST'])
def main_page():
    if current_user.is_authenticated:
        return redirect(url_for('auth_routes.dashboard'))
    else:
        return redirect(url_for('auth_routes.login'))

@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth_routes.dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')
        
        if users.checkUser(username):
            try:
                users.register_user(username, password, role)
                flash('Регистрация прошла успешно! Пожалуйста, войдите.', 'success')
                return redirect(url_for('auth_routes.login'))
            except Exception as e:
                flash('Произошла ошибка при регистрации.', 'error')
                print(f"Registration error: {e}")
        else:
            flash('Имя пользователя уже существует. Выберите другое.', 'error')
    
    return render_template('register.html')

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth_routes.dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users.login_user(username, password)
        if user:
            login_user(user)
            return redirect(url_for('auth_routes.dashboard'))
        else:
            flash('Неверное имя пользователя или пароль.', 'error')
    
    return render_template('login.html')

@auth_routes.route('/')
@auth_routes.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM requests WHERE user_id = ?", (current_user.id,))
    user_requests = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM requests WHERE status != 'resolved' AND status != 'closed'")
    total_incidents = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('dashboard.html',
                         total_requests=user_requests,
                         user_requests=user_requests,
                         total_users=total_users,
                         total_incidents=total_incidents)

@auth_routes.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        
        user = users.login_user(current_user.username, current_password)
        if not user:
            flash('Неверный текущий пароль.', 'error')
            return redirect(url_for('auth_routes.settings'))
        
        try:
            password_hash = users.hash_password(new_password)
            conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, current_user.id))
            conn.commit()
            conn.close()
            flash('Пароль успешно изменён.', 'success')
        except Exception as e:
            flash('Ошибка при изменении пароля.', 'error')
            print(f"Change password error: {e}")
        
        return redirect(url_for('auth_routes.settings'))
    
    return render_template('settings.html')

@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_routes.login'))