import redis
from flask import Flask
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models.db_models.user import db
from routes.authentication import authentication
from routes.settings import settings
from routes.fetch_user_data import fetch_user_data


def init_jwt_token_loader(jwt, redis_client):
    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]

        return redis_client.exists(jti) > 0


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
    app.register_blueprint(fetch_user_data, url_prefix="/dvi-api/fetch-user-data")
    app.register_blueprint(settings, url_prefix="/dvi-api/settings")
    
    init_jwt_token_loader(jwt, redis_client)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
