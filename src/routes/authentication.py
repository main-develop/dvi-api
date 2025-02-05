from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from models.db_models.user import db, User
from models.pydantic_models.user import AuthenticateUser
from pydantic import ValidationError
from datetime import timedelta

authentication = Blueprint("authentication", __name__)


@authentication.route("/register", methods=["POST"])
def register():
    try:
        data = AuthenticateUser(**request.json)
    except ValidationError as error:
        details: dict = dict(list(error.errors()[0].items())[:-1])

        return jsonify({"message": "Failed to register a user.", "error": details}), 400
    
    if User.query.filter_by(email=data.email).first():
        return jsonify({"message": "This email address is already taken"}), 400

    new_user = User(
        first_name=data.firstName,
        last_name=data.lastName,
        email=data.email,
        gender=data.gender
    )
    new_user.password = data.password.get_secret_value()

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@authentication.route("/login", methods=["POST"])
def login():
    try:
        data = AuthenticateUser(**request.json)
    except ValidationError as error:
        details: dict = dict(list(error.errors()[0].items())[:-1])

        return jsonify({"message": "Failed to log in a user.", "error": details}), 400

    user = User.query.filter_by(email=data.email).first()

    if not user or not user.check_password(data.password.get_secret_value()):
        return jsonify({"message": "Invalid email or password"}), 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=5) if data.rememberMe else None)

    return jsonify({"message": "Successfully logged in", "accessToken": access_token}), 200


@authentication.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]

    redis_client = current_app.redis_client
    redis_client.set(jti, "", ex=timedelta(days=2))

    return jsonify({"message": "Successfully logged out"}), 200
