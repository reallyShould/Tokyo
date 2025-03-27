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
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('auth_routes.dashboard'))
        else:
            flash('Неверное имя пользователя или пароль.', 'error')
    
    return render_template('login.html')

@auth_routes.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM requests WHERE user_id = ? AND status != 'closed'", (current_user.id,))
    requests_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    
    incidents_count = 0
    if current_user.is_specialist():
        cursor.execute("SELECT COUNT(*) FROM requests WHERE status == 'open'")
        incidents_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT fullname FROM users WHERE username = ?", (current_user.username,))
    fullname = cursor.fetchall()[0][0]
    conn.close()
    
    return render_template('dashboard.html', 
                         users_count=users_count,
                         requests_count=requests_count,
                         incidents_count=incidents_count,
                         username=current_user.username,
                         fullname=fullname,
                         is_specialist=current_user.is_specialist())

@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('auth_routes.login'))