from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import UserService

user = Blueprint('user', __name__)

@user.route('user/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Thiếu thông tin.'}), 400

    user, message = UserService.register_user(username, email, password)
    if user:
        return jsonify({'message': message}), 201
    else:
        return jsonify({'message': message}), 409

@user.route('user/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({"message": "Thiếu thông tin"}), 400

    access_token, message = UserService.login(email, password)
    if access_token:
        return jsonify(message=message, access_token=access_token), 200
    else:
        return jsonify({"message": message}), 401

@user.route('user/delete', methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user_id = get_jwt_identity()['id']
    success, message = UserService.delete_user(current_user_id)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": message}), 500

@user.route('user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    current_user_id = get_jwt_identity()['id']
    user, message = UserService.get_user_by_id(current_user_id)
    if user:
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        }), 200
    else:
        return jsonify({"message": message}), 404

@user.route('user/update', methods=['PUT'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()['id']
    data = request.json
    user, message = UserService.update_user(current_user_id, data)
    if user:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": message}), 400

@user.route('user/all', methods=['GET'])
@jwt_required()
def get_all_users():
    users, message = UserService.get_all_users()
    return jsonify({
        "message": message,
        "users": [{"id": user.id, "username": user.username, "email": user.email} for user in users]
    }), 200

@user.route('user/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()['id']
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({"message": "Thiếu thông tin"}), 400
    
    success, message = UserService.change_password(current_user_id, old_password, new_password)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": message}), 400
