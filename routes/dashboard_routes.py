from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_routes = Blueprint('dashboard_routes', __name__)

@dashboard_routes.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)
