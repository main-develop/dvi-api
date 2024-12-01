from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User

authentication = Blueprint("authentication", __name__)


@authentication.route("/register", methods=["POST"])
def register():
    data = request.json

    if "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email or password."}), 400

    first_name = data.get("firstName")
    last_name = data.get("lastName")
    email = data["email"]
    password = data["password"]
    gender = data.get("gender", "Rather not say")

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "User with this email already exists."}), 400

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

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401
    
    access_token = create_access_token(identity=user.id)

    return jsonify({"message": "Login successful.", "access_token": access_token}), 200
