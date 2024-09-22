import os
from flask import current_app
from werkzeug.utils import secure_filename
from api.model import Folder, File
from api.extension import db
import logging

logger = logging.getLogger(__name__)

class FolderService:
    @staticmethod
    def create_folder(folder_name, parent_folder_id, current_user):
        folder_name = secure_filename(folder_name)
        new_folder = Folder(
            name=folder_name,
            parent_id=parent_folder_id,
            user_id=current_user['id']
        )
        db.session.add(new_folder)
        db.session.commit()
        return {"id": new_folder.id, "name": new_folder.name}

    @staticmethod
    def get_folder_contents(folder_id, current_user):
        folder = Folder.query.get(folder_id)
        if folder and folder.user_id == current_user['id']:
            subfolders = Folder.query.filter_by(parent_id=folder_id).all()
            files = File.query.filter_by(folder_id=folder_id).all()
            return {
                "folder": {
                    "id": folder.id,
                    "name": folder.name,
                    "created_at": folder.created_at
                },
                "subfolders": [
                    {"id": sf.id, "name": sf.name, "created_at": sf.created_at}
                    for sf in subfolders
                ],
                "files": [
                    {
                        "id": f.id,
                        "name": f.name,
                        "uploaded_at": f.uploaded_at,
                        "size": os.path.getsize(os.path.join(current_app.config['UPLOAD_FOLDER'], f.name)),
                    }
                    for f in files
                ]
            }
        return None

    @staticmethod
    def get_all_folders(current_user):
        folders = Folder.query.filter_by(user_id=current_user['id']).all()
        return [
            {
                "id": folder.id,
                "name": folder.name,
                "created_at": folder.created_at,
                "parent_id": folder.parent_id
            } for folder in folders
        ]

    @staticmethod
    def delete_folder(folder_id, current_user):
        folder = Folder.query.get(folder_id)
        if folder and folder.user_id == current_user['id']:
            # Xóa tất cả các file trong thư mục
            files = File.query.filter_by(folder_id=folder_id).all()
            for file in files:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], file.name))
                except OSError as e:
                    logger.error(f"Error deleting file: {e}")
                db.session.delete(file)

            # Xóa đệ quy tất cả các thư mục con
            subfolders = Folder.query.filter_by(parent_id=folder_id).all()
            for subfolder in subfolders:
                FolderService.delete_folder(subfolder.id, current_user)

            db.session.delete(folder)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update_folder_info(folder_id, new_name, current_user):
        folder = Folder.query.get(folder_id)
        if folder and folder.user_id == current_user['id']:
            folder.name = secure_filename(new_name)
            db.session.commit()
            return True
        return False

    @staticmethod
    def move_folder(folder_id, new_parent_id, current_user):
        folder = Folder.query.get(folder_id)
        new_parent = Folder.query.get(new_parent_id) if new_parent_id else None
        if folder and folder.user_id == current_user['id'] and (not new_parent or new_parent.user_id == current_user['id']):
            folder.parent_id = new_parent_id
            db.session.commit()
            return True
        return False
