from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
import sqlite3
import config

incidents_bp = Blueprint('incidents', __name__)

@incidents_bp.route('/incidents')
@login_required
def list_incidents():
    if not current_user.is_admin():
        abort(403)
    
    conn = sqlite3.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status, created_at FROM incidents WHERE status != 'resolved'")
    incidents = cursor.fetchall()
    conn.close()
    return render_template('incidents.html', incidents=incidents)