import os
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, current_user, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from api.model import User
from api import webserver_ma
from api.extension import db
import logging

logger = logging.getLogger(__name__)
user_schema = webserver_ma.UserSchema
users_schema = webserver_ma.UserSchema(many=True)

class UserService:
    @staticmethod
    def register_user(username, email, password):
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return None, "Tên người dùng hoặc email đã tồn tại."

        hashed_password = generate_password_hash(password)
        try:
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(new_user.id))
            os.makedirs(user_folder, exist_ok=True)
            return new_user, "Đăng ký người dùng thành công."
        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi xảy ra khi tạo người dùng: {str(e)}")
            return None, "Lỗi xảy ra khi tạo người dùng."

    @staticmethod
    def login(email, password):
        user = User.query.filter_by(email=email).first()
        if not user:
            logger.error("Không tìm thấy người dùng")
            return None, "Thông tin đăng nhập không hợp lệ"

        if not check_password_hash(user.password, password):
            logger.error("Mật khẩu không đúng")
            return None, "Thông tin đăng nhập không hợp lệ"

        access_token = create_access_token(identity={"id": user.id, "name": user.username})
        logger.info(f'Người dùng đã đăng nhập: {user.username} (ID: {user.id})')
        return access_token, "Đăng nhập thành công."

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return False, "Không tìm thấy người dùng"
        try:
            db.session.delete(user)
            db.session.commit()
            return True, "Xóa người dùng thành công."
        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi xảy ra khi xóa người dùng: {str(e)}")
            return False, "Lỗi xảy ra khi xóa người dùng."

    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        if user:
            return user, "Tìm thấy người dùng."
        return None, "Không tìm thấy người dùng."

    @staticmethod
    def update_user(user_id, data):
        user = User.query.get(user_id)
        if not user:
            return None, "Không tìm thấy người dùng."
        
        try:
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'password' in data:
                user.password = generate_password_hash(data['password'])
            
            db.session.commit()
            return user, "Cập nhật người dùng thành công."
        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi xảy ra khi cập nhật người dùng: {str(e)}")
            return None, "Lỗi xảy ra khi cập nhật người dùng."

    @staticmethod
    def get_all_users():
        users = User.query.all()
        return users, "Lấy danh sách người dùng thành công."

    @staticmethod
    def change_password(user_id, old_password, new_password):
        user = User.query.get(user_id)
        if not user:
            return False, "Không tìm thấy người dùng."
        
        if not check_password_hash(user.password, old_password):
            return False, "Mật khẩu cũ không đúng."
        
        try:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            return True, "Thay đổi mật khẩu thành công."
        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi xảy ra khi thay đổi mật khẩu: {str(e)}")
            return False, "Lỗi xảy ra khi thay đổi mật khẩu."

