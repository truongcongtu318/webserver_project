import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.environ.get('KEY')
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH'))
SQLALCHEMY_TRACK_MODIFICATIONS = False