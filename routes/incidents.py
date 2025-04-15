from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
import sqlite3
import config
from format_table import change_names

incidents_bp = Blueprint('incidents', __name__)

@incidents_bp.route('/incidents')
@login_required
def list_incidents():
    if not current_user.is_specialist():
        abort(403)
    
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status, created_at, user_id FROM requests WHERE status != 'resolved' AND status != 'closed'")
    incidents = [dict(row) for row in cursor.fetchall()]
    
    for incident in incidents:
        cursor.execute("SELECT username, fullname FROM users WHERE id = ?", (incident["user_id"],))
        user = cursor.fetchone()
        incident["username"] = f"{user[1] if user[1] else user[0]}" if user else "Неизвестный пользователь"
    
    conn.close()
    
    incidents = change_names(incidents)
    
    return render_template('incidents.html', incidents=incidents)

@incidents_bp.route('/incidents/<int:incident_id>')
@login_required
def view_incident(incident_id):
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, description, status, created_at, user_id, resolution FROM requests WHERE id = ?", (incident_id,))
    incident = cursor.fetchone()
    
    if not incident:
        conn.close()
        abort(404)
    
    if not (current_user.is_specialist() or incident["user_id"] == current_user.id):
        conn.close()
        abort(403)
    
    cursor.execute("SELECT username, fullname FROM users WHERE id = ?", (incident["user_id"],))
    user = cursor.fetchone()
    creator_username = f"{user[1] if user[1] else user[0]}" if user else "Неизвестный пользователь"
    
    conn.close()
    
    incident = dict(incident)
    incident = change_names([incident])[0]
    
    return render_template('incident_detail.html', 
                         incident=incident,
                         creator_username=creator_username,
                         is_specialist=current_user.is_specialist())

@incidents_bp.route('/resolve_incident/<int:incident_id>', methods=['GET', 'POST'])
@login_required
def resolve_incident(incident_id):
    if not current_user.is_specialist():
        abort(403)
    
    if request.method == 'POST':
        resolution = request.form['resolution']
        
        if not resolution:
            flash('Описание решения обязательно!', 'error')
            return redirect(url_for('incidents.view_incident', incident_id=incident_id))
        
        try:
            conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
            cursor = conn.cursor()
            cursor.execute("UPDATE requests SET status = 'resolved', resolution = ? WHERE id = ?", (resolution, incident_id))
            conn.commit()
            conn.close()
            flash('Инцидент успешно решён.', 'success')
            return redirect(url_for('incidents.list_incidents'))
        except Exception as e:
            flash('Ошибка при решении инцидента.', 'error')
            print(f"Resolve incident error: {e}")
            return redirect(url_for('incidents.view_incident', incident_id=incident_id))
    
    return render_template('resolve_incident.html', incident_id=incident_id)
