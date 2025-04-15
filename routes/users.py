from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
import sqlite3
import config
from format_table import change_spec, check_none

users_bp = Blueprint('users', __name__)

@users_bp.route("/users")
@login_required
def list_users():
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, fullname, mail, role FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    users = check_none(users)
    users = change_spec(users)
    
    return render_template('users.html',
                           users=users,
                           is_specialist=current_user.is_specialist())

@users_bp.route('/users/<int:user_id>')
@login_required
def view_user(user_id):
    if not current_user.is_specialist():
        abort(403)
    
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, fullname, mail, role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        abort(404)
    
    conn.close()
    
    user = dict(user)
    user = check_none([user])[0]
    user = change_spec([user])[0]
    
    return render_template('user_detail.html', 
                           user=user,
                           is_specialist=current_user.is_specialist())

@users_bp.route('/users/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    if not current_user.is_specialist():
        abort(403)
    
    fullname = request.form['fullname'].strip() or None
    username = request.form['username'].strip()
    mail = request.form['mail'].strip() or None
    role = request.form['role'].strip() or None
    
    if not username:
        flash('Имя пользователя обязательно!', 'error')
        return redirect(url_for('users.view_user', user_id=user_id))
    
    if role not in ['user', 'admin', 'system-adm']:
        flash('Недопустимая роль!', 'error')
        return redirect(url_for('users.view_user', user_id=user_id))
    
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (username, user_id))
    if cursor.fetchone():
        conn.close()
        flash('Имя пользователя уже занято!', 'error')
        return redirect(url_for('users.view_user', user_id=user_id))
    
    try:
        cursor.execute("UPDATE users SET fullname = ?, username = ?, mail = ?, role = ? WHERE id = ?", 
                       (fullname, username, mail, role, user_id))
        conn.commit()
        flash('Данные пользователя успешно обновлены!', 'success')
    except Exception as e:
        flash('Ошибка при обновлении данных пользователя.', 'error')
        print(f"Update user error: {e}")
    
    conn.close()
    return redirect(url_for('users.view_user', user_id=user_id))