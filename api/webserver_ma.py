from .extension import ma

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "email","password")

class FolderSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "path", "created_at", "parent_id", "user_id")

class FileSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "path", "uploaded_at", "folder_id", "user_id")

class LogSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "action", "target_id", "target_type", "timestamp")

class SharedFileSchema(ma.Schema):
    class Meta:
        fields = ("id", "file_id", "owner_id", "shared_with_id")

class SharedFolderSchema(ma.Schema):
    class Meta:
        fields = ("id", "folder_id", "owner_id", "shared_with_id")