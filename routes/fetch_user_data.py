from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User

fetch_user_data = Blueprint("fetch_user_data", __name__)


@fetch_user_data.route("/get-user-personal-information", methods=["GET"])
@jwt_required()
def get_user_personal_information():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "message": "User personal information fetched successfully",
        "user": {
            "firstName": user.first_name,
            "lastName": user.last_name,
            "gender": user.gender,
            "email": user.email,
        }
    }), 200
