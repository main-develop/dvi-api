from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User
from datetime import timedelta

settings = Blueprint("settings", __name__)


@settings.route("/change-personal-information", methods=["PUT"])
@jwt_required()
def change_personal_information():
    data = request.json

    first_name = data.get("firstName")
    last_name = data.get("lastName")
    gender = data.get("gender", "Rather not say")

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if user.first_name != first_name:
        user.first_name = first_name

    if user.last_name != last_name:
        user.last_name = last_name

    if user.gender != gender:
        user.gender = gender
    db.session.commit()

    return jsonify({
        "message": "Personal information changed successfully.",
    }), 200


@settings.route("/change-email", methods=["PUT"])
@jwt_required()
def change_email():
    data = request.json

    email = data["email"]
    password = data["password"]

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "This email address is already taken"}), 400
    if not user.check_password(password):
        return jsonify({"message": "Invalid password"}), 403
    
    user.email = email
    db.session.commit()

    return jsonify({
        "message": "A confirmation email has been sent.",
    }), 200


@settings.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    new_password = request.json["newPassword"]
    old_password = request.json["oldPassword"]

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404
    if not user.check_password(old_password):
        return jsonify({"message": "Invalid password"}), 403
    
    user.password = new_password
    db.session.commit()

    return jsonify({"message": "Password changed successfully."}), 200


@settings.route("/delete-account", methods=["DELETE"])
@jwt_required()
def delete_account():
    password = request.json["password"]

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404
    if not user.check_password(password):
        return jsonify({"message": "Invalid password"}), 403
    
    db.session.delete(user)
    db.session.commit()

    jti = get_jwt()["jti"]

    redis_client = current_app.redis_client
    redis_client.set(jti, "", ex=timedelta(days=2))

    return jsonify({"message": "Account successfully deleted"}), 200
