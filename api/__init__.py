from flask import Flask, request, jsonify, g
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from flask_cors import CORS
from api.user.controller import user
from api.views.controller import views
from api.file.controller import file
from api.extension import ma, db
from api.model import User
import logging
import os
from http import HTTPStatus
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

def create_db(app):
    if not os.path.exists('webserver_project/webserver.db'):
        with app.app_context():
            db.create_all()
            app.logger.info('Cơ sở dữ liệu được tạo thành công')

def create_app(config='config.py'):
    app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'),
                        static_folder=os.path.join(os.getcwd(), 'static'))
    
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    app.config.from_pyfile(config)
    
    db.init_app(app)
    ma.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    create_db(app)

    @app.before_request
    def identify_user():
        app.logger.debug("Starting identify_user")
        g.user_info = "Anonymous User"
        try:
            app.logger.debug("Verifying JWT")
            verify_jwt_in_request(optional=True)
            app.logger.debug("Getting JWT identity")
            current_user = get_jwt_identity()
            app.logger.debug(f"Current user: {current_user}")
            if current_user and isinstance(current_user, dict):
                user_id = current_user.get('id')
                user_name = current_user.get('name')
                if user_id and user_name:
                    g.user_info = f"User: {user_name} (ID: {user_id})"
                else:
                    app.logger.warning(f"Incomplete user information in JWT: {current_user}")
                    g.user_info = f"Incomplete User Info: {current_user}"
            else:
                app.logger.debug("No valid user information found in JWT")
        except ExpiredSignatureError:
            app.logger.warning("Token has expired")
            g.user_info = "Expired Token User"
        except InvalidTokenError:
            app.logger.warning("Invalid token provided")
            g.user_info = "Invalid Token User"
        except Exception as e:
            app.logger.error(f"Error in identify_user: {str(e)}", exc_info=True)
            g.user_info = "Error Identifying User"
        app.logger.debug(f"Final user_info: {g.user_info}")

    @app.after_request
    def log_request_info(response):
        status_code = response.status_code
        status_phrase = HTTPStatus(status_code).phrase
        app.logger.info(f"{g.user_info} - {request.remote_addr} - {request.method} {request.url} - Status: {status_code} {status_phrase}")
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the exception
        app.logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
        # Return JSON instead of HTML for HTTP errors
        return jsonify(error=str(e)), 500

    app.register_blueprint(user, url_prefix='/api')
    app.register_blueprint(views)
    app.register_blueprint(file, url_prefix='/api')
    
    app.logger.info('Ứng dụng đã được khởi tạo thành công')
    
    return app