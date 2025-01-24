from flask import Flask
from flask_login import LoginManager
from models import db
from routes import auth_routes, dashboard_routes
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Регистрируем маршруты
app.register_blueprint(auth_routes)
app.register_blueprint(dashboard_routes)

if __name__ == '__main__':
    app.run(debug=True)
