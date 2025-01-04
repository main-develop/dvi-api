from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from models import db, User
from datetime import timedelta

authentication = Blueprint("authentication", __name__)


@authentication.route("/register", methods=["POST"])
def register():
    data = request.json

    first_name = data.get("firstName")
    last_name = data.get("lastName")
    email = data["email"]
    password = data["password"]
    gender = data.get("gender", "Rather not say")

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "This email address is already taken."}), 400

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        gender=gender
    )
    new_user.password = password

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully."}), 201


@authentication.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data["email"]
    password = data["password"]
    remember_me = data["rememberMe"]

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password."}), 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=5) if remember_me else None)

    return jsonify({"message": "Login successful.", "accessToken": access_token}), 200


@authentication.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]

    redis_client = current_app.redis_client
    redis_client.set(jti, "", ex=timedelta(days=2))

    return jsonify({"message": "Successfully logged out."}), 200
