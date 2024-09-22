from datetime import datetime
import os
from flask import current_app, url_for
from werkzeug.utils import secure_filename
from api.model import File
from api.extension import db
import logging

logger = logging.getLogger(__name__)

class FileService:
    @staticmethod
    def upload_file(file, current_user):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user['id']))
            os.makedirs(user_folder, exist_ok=True)

            base_name, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(user_folder, filename)):
                filename = f"{base_name}_{counter}{extension}"
                counter += 1

            upload_path = os.path.join(user_folder, filename)
            file.save(upload_path)
            file_url = url_for('file.download_file', filename=filename, user_id=current_user['id'], _external=True)

            new_file = File(
                name=filename,
                path=file_url,
                uploaded_at=datetime.utcnow(),
                user_id=current_user['id']
            )
            db.session.add(new_file)
            db.session.commit()

            return {"filename": filename, "file_url": file_url}
        return None

    @staticmethod
    def get_file(filename, current_user):
        if not current_user or 'id' not in current_user:
            return None
        file_record = File.query.filter_by(name=filename, user_id=current_user['id']).first()
        if file_record:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user['id']), filename)
            return file_path
        return None

    @staticmethod
    def get_all_files(current_user):
        files = File.query.filter_by(user_id=current_user['id']).all()
        user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user['id']))
        return [
            {
                "id": file.id,
                "name": file.name,
                "uploaded_at": file.uploaded_at,
                "size": os.path.getsize(os.path.join(user_folder, file.name)),
                "path": file.path,
            } for file in files if os.path.exists(os.path.join(user_folder, file.name))
        ]

    @staticmethod
    def delete_file(file_id, current_user):
        file_record = File.query.get(file_id)
        if file_record and file_record.user_id == current_user['id']:
            try:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user['id']), file_record.name)
                os.remove(file_path)
            except OSError as e:
                logger.error(f"Error deleting file: {e}")
            db.session.delete(file_record)
            db.session.commit()
            return True
        return False

    @staticmethod
    def update_file_info(file_id, new_name, current_user):
        file_record = File.query.get(file_id)
        if file_record and file_record.user_id == current_user['id']:
            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user['id']), file_record.name)
            new_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user['id']), new_name)
            try:
                os.rename(old_path, new_path)
                file_record.name = new_name
                file_record.path = url_for('file.download_file', filename=new_name, user_id=current_user['id'], _external=True)
                db.session.commit()
                return True
            except OSError as e:
                logger.error(f"Error renaming file: {e}")
                return False
        return False

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'zip', 'rar'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS