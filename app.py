from flask import Flask, render_template
from flask_login import LoginManager
from models import Users
from routes import auth_routes, requests, incidents, users_list
from config import Config
import format_table

app = Flask(__name__, )
app.config.from_object(Config)

app.jinja_env.globals['get_username'] = Users.get_username_by_id
app.jinja_env.globals['change_names'] = format_table.change_names
app.jinja_env.globals['change_spec'] = format_table.change_spec
app.jinja_env.globals['view_incident'] = incidents.view_incident
app.jinja_env.globals['get_fullname'] = Users.get_fullname_by_id
app.jinja_env.globals['check_none'] = format_table.check_none

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_routes.login"

@login_manager.user_loader
def load_user(user_id):
    users = Users()
    return users.get_user_by_id(user_id)

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

users = Users()
users.init_db()

app.register_blueprint(auth_routes)
app.register_blueprint(requests.requests_bp)
app.register_blueprint(incidents.incidents_bp)
app.register_blueprint(users_list.users_bp)

if __name__ == '__main__':
    app.run(debug=True, host=Config.HOST, port=Config.PORT)