from flask import Flask
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import os
from sqlalchemy.pool import StaticPool

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO(async_mode="eventlet", cors_allowed_origins="*")

def create_app():
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        template_folder="templates"
    )
    app.config.from_object(Config)

    # Make instance and upload folders
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Override SQLAlchemy engine options to be Eventlet-friendly
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool
    }

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    socketio.init_app(app)

    # Import and register blueprints
    from .models import User
    from .auth import auth_bp
    from .main import main_bp
    from .chat import chat_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)

    # Register SocketIO handlers
    from .chat import register_socketio_handlers
    register_socketio_handlers(socketio)

    # Create DB tables inside app context
    with app.app_context():
        db.create_all()

    return app
