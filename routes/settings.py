from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.db_models.user import db, User
from models.pydantic_models.user import UpdateUser, ChangeUserEmail, ChangeUserPassword, DeleteUser
from pydantic import ValidationError
from datetime import timedelta

settings = Blueprint("settings", __name__)


@settings.route("/change-personal-information", methods=["PUT"])
@jwt_required()
def change_personal_information():
    try:
        data = UpdateUser(**request.json)
    except ValidationError as error:
        details: dict = dict(list(error.errors()[0].items())[:-1])

        return jsonify({"message": "Failed to change personal information.", "error": details}), 400

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if user.first_name != data.firstName:
        user.first_name = data.firstName

    if user.last_name != data.lastName:
        user.last_name = data.lastName

    if user.gender != data.gender:
        user.gender = data.gender
    db.session.commit()

    return jsonify({"message": "Personal information changed successfully."}), 200


@settings.route("/change-email", methods=["PUT"])
@jwt_required()
def change_email():
    try:
        data = ChangeUserEmail(**request.json)
    except ValidationError as error:
        details: dict = dict(list(error.errors()[0].items())[:-1])

        return jsonify({"message": "Failed to change email.", "error": details}), 400

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404
    if User.query.filter_by(email=data.email).first():
        return jsonify({"message": "This email address is already taken"}), 400
    if not user.check_password(data.password.get_secret_value()):
        return jsonify({"message": "Invalid password"}), 403
    
    user.email = data.email
    db.session.commit()

    return jsonify({"message": "A confirmation email has been sent."}), 200


@settings.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    try:
        data = ChangeUserPassword(**request.json)
    except ValidationError as error:
        details: dict = dict(list(error.errors()[0].items())[:-1])

        return jsonify({"message": "Failed to change password.", "error": details}), 400

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404
    if not user.check_password(data.oldPassword.get_secret_value()):
        return jsonify({"message": "Invalid password"}), 403
    
    user.password = data.newPassword.get_secret_value()
    db.session.commit()

    return jsonify({"message": "Password changed successfully."}), 200


@settings.route("/delete-account", methods=["DELETE"])
@jwt_required()
def delete_account():
    try:
        data = DeleteUser(**request.json)
    except ValidationError as error:
        details: dict = dict(list(error.errors()[0].items())[:-1])

        return jsonify({"message": "Failed to delete account.", "error": details}), 400

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404
    if not user.check_password(data.password.get_secret_value()):
        return jsonify({"message": "Invalid password"}), 403
    
    db.session.delete(user)
    db.session.commit()

    jti = get_jwt()["jti"]

    redis_client = current_app.redis_client
    redis_client.set(jti, "", ex=timedelta(days=2))

    return jsonify({"message": "Account successfully deleted"}), 200
