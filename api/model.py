from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .extension import db


# Bảng users: Lưu trữ thông tin người dùng
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    folders = db.relationship('Folder', backref='owner', lazy=True)
    files = db.relationship('File', backref='owner', lazy=True)

    shared_files = db.relationship(
        'SharedFile', foreign_keys='SharedFile.shared_with_id', backref='shared_with', lazy='dynamic'
    )
    shared_folders = db.relationship(
        'SharedFolder', foreign_keys='SharedFolder.shared_with_id', backref='shared_with', lazy='dynamic'
    )


# Bảng folders: Lưu trữ thông tin các thư mục mà người dùng tạo
class Folder(db.Model):
    __tablename__ = 'folders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Quan hệ đệ quy với folder cha
    parent_folder = db.relationship('Folder', remote_side=[id], backref='subfolders')
    files = db.relationship('File', backref='folder', lazy=True)

    shared_folders = db.relationship('SharedFolder', backref='folder', lazy='dynamic')


# Bảng files: Lưu trữ thông tin các file mà người dùng tải lên
class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    shared_files = db.relationship('SharedFile', backref='file', lazy='dynamic')


# Bảng logs: Ghi lại các hành động của người dùng
class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    target_type = db.Column(db.String(50), nullable=False)  # 'file' hoặc 'folder'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='logs')


# Bảng shared_files: Lưu thông tin về file được chia sẻ giữa người dùng
class SharedFile(db.Model):
    __tablename__ = 'shared_files'

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_files')


# Bảng shared_folders: Lưu thông tin về thư mục được chia sẻ giữa người dùng
class SharedFolder(db.Model):
    __tablename__ = 'shared_folders'

    id = db.Column(db.Integer, primary_key=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_folders')