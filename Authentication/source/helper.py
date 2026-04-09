from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import Role, database, User

helper_bp = Blueprint("helper", __name__)

@helper_bp.route("/check_alive", methods=["GET"])
def check_alive():
    return "Alive"
@helper_bp.route("/check_token", methods=["GET"])
@jwt_required()
def check_token():
    return "Token check"

@helper_bp.route("/get_user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    return jsonify(str(user))

@helper_bp.route("/get_all_users", methods=["GET"])
def get_all_users():
    return jsonify ([str(user) for user in User.query.all()])

@helper_bp.route("/get_all_roles", methods=["GET"])
def get_all_roles():
    return jsonify ([str(role) for role in Role.query.all()])

@helper_bp.route("/delete_data", methods=["DELETE"])
def delete_data():
    User.query.filter(User.email != "onlymoney@gmail.com").delete()
    database.session.commit()
    return "Deleted all users"
