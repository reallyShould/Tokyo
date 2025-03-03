from flask import Flask
from flask_login import LoginManager
from models import Users
from routes import auth_routes, dashboard_routes
from config import Config

users = Users()
users.init_db()

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_routes)
app.register_blueprint(dashboard_routes)

if __name__ == '__main__':
    app.run(debug=True)
