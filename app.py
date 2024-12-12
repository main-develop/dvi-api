from flask import Flask
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import redis

from config import Config
from models import db
from routes.authentication import authentication, init_jwt_token_loader


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    bcrypt = Bcrypt(app)
    CORS(app)

    jwt = JWTManager(app)

    redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
    app.redis_client = redis_client

    app.register_blueprint(authentication, url_prefix="/dvi-api/authentication")
    init_jwt_token_loader(jwt)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
