from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user
from models import db, User

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует!', 'danger')
            return redirect(url_for('auth_routes.register'))
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Регистрация успешна! Вы можете войти в свой аккаунт.', 'success')
        return redirect(url_for('auth_routes.login'))
    
    return render_template('register.html')

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard_routes.dashboard'))
        
        flash('Неправильный логин или пароль.', 'danger')
    
    return render_template('login.html')
