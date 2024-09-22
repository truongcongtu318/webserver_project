import os
from flask import Blueprint, current_app, jsonify, request, send_from_directory, send_file, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from .service import FileService

file = Blueprint('file', __name__)

@file.route('file/upload', methods=['POST'])
@jwt_required()
def upload_file():

    if 'file' not in request.files:
        return jsonify({"message": "Không có phần file"}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({"message": "Không có file được chọn"}), 400

    current_user = get_jwt_identity()
    result = FileService.upload_file(uploaded_file, current_user)
    if result:
        return jsonify({
            "message": "File đã được tải lên thành công",
            "filename": result["filename"],
            "file_url": result["file_url"]
        }), 201
    else:
        return jsonify({"message": "Loại file không được phép"}), 400

@file.route('file/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    try:
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        print(current_user)
        if not current_user or 'id' not in current_user:
            abort(401, description="Unauthorized")

        file_path = FileService.get_file(filename, current_user)
        if file_path and os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            abort(404, description="File không tồn tại")
    except Exception as e:
        current_app.logger.error(f"Error in download_file: {str(e)}")
        return jsonify({"error": "Có lỗi xảy ra khi tải file"}), 500
@file.route('file/list', methods=['GET'])
@jwt_required()
def list_files():

    current_user = get_jwt_identity()
    files = FileService.get_all_files(current_user)
    return jsonify({"files": files}), 200

@file.route('file/delete/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):

    current_user = get_jwt_identity()
    if FileService.delete_file(file_id, current_user):
        return jsonify({"message": "File đã được xóa thành công"}), 200
    return jsonify({"message": "File không tìm thấy hoặc không có quyền truy cập"}), 404

@file.route('file/update/<int:file_id>', methods=['PUT'])
@jwt_required()
def update_file_info(file_id):

    current_user = get_jwt_identity()
    data = request.json
    if 'name' in data and FileService.update_file_info(file_id, data['name'], current_user):
        return jsonify({"message": "Thông tin file đã được cập nhật thành công"}), 200
    return jsonify({"message": "File không tìm thấy hoặc không có quyền truy cập"}), 404