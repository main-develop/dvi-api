from flask import Flask
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from config import Config
from models import db
from routes.authentication import authentication


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(authentication, url_prefix="/dvi-api/authentication")

    db.init_app(app)

    migrate = Migrate(app, db)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)