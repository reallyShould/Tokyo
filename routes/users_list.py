from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
import sqlite3
import config
from format_table import change_names

users_bp = Blueprint('users', __name__)

@users_bp.route("/users")
@login_required
def list_users():
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, fullname, mail, role FROM users")
    users = cursor.fetchall()

    conn.close()
    
    return render_template('users.html',
                           users=users,
                           is_specialist=current_user.is_specialist())

@users_bp.route('/users/<int:user_id>')
@login_required
def view_user(user_id):
    if not current_user.is_specialist():
        abort(403)
    
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = cursor.fetchone()[0]
    cursor.execute("SELECT fullname FROM users WHERE id = ?", (user_id,))
    fullname = cursor.fetchone()[0]
    cursor.execute("SELECT mail FROM users WHERE id = ?", (user_id,))
    mail = cursor.fetchone()[0]
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    role = cursor.fetchone()[0]
    conn.close()
    
    return render_template('user_detail.html', 
                           users=users,
                           user_id=user_id,
                           username=username, 
                           fullname=fullname, 
                           mail=mail, 
                           role=role, 
                           is_specialist=current_user.is_specialist())

@users_bp.route('/users/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    if not current_user.is_specialist():
        abort(403)
    
    fullname = request.form['fullname'] or None
    username = request.form['username']
    mail = request.form['mail'] or None
    role = request.form['role'] or None
    
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET fullname = ?, username = ?, mail = ?, role = ? WHERE id = ?", 
                   (fullname, username, mail, role, user_id))
    conn.commit()
    conn.close()
    
    flash('Данные пользователя успешно обновлены!', 'success')
    return redirect(url_for('users.view_user', user_id=user_id))