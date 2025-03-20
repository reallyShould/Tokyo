from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlite3
import config

requests_bp = Blueprint('requests', __name__)

@requests_bp.route('/requests')
@login_required
def list_requests():
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status, created_at FROM requests WHERE user_id = ? AND status != 'closed'", (current_user.id,))
    requests = cursor.fetchall()
    conn.close()
    return render_template('requests.html', requests=requests)

@requests_bp.route('/create_request', methods=['GET', 'POST'])
@login_required
def create_request():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        if not title:
            flash('Название заявки обязательно!', 'error')
            return render_template('create_request.html')
        
        try:
            conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO requests (user_id, title, description) VALUES (?, ?, ?)",
                         (current_user.id, title, description))
            conn.commit()
            conn.close()
            flash('Заявка успешно создана!', 'success')
            return redirect(url_for('requests.list_requests'))
        except Exception as e:
            flash('Ошибка при создании заявки.', 'error')
            print(f"Create request error: {e}")
            return render_template('create_request.html')
    
    return render_template('create_request.html')

@requests_bp.route('/close_request/<int:request_id>', methods=['POST'])
@login_required
def close_request(request_id):
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    cursor = conn.cursor()
    
    # Проверяем, что запрос принадлежит текущему пользователю
    cursor.execute("SELECT user_id FROM requests WHERE id = ?", (request_id,))
    request = cursor.fetchone()
    
    if not request or request[0] != current_user.id:
        conn.close()
        flash('У вас нет прав для закрытия этой заявки.', 'error')
        return redirect(url_for('requests.list_requests'))
    
    try:
        cursor.execute("UPDATE requests SET status = 'closed' WHERE id = ?", (request_id,))
        conn.commit()
        flash('Заявка успешно закрыта.', 'success')
    except Exception as e:
        flash('Ошибка при закрытии заявки.', 'error')
        print(f"Close request error: {e}")
    
    conn.close()
    return redirect(url_for('requests.list_requests'))