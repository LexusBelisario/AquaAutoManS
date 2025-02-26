import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_caching import Cache
from app.utils.limiters import limiter
from logging.handlers import RotatingFileHandler

# Initialize extensions
db = SQLAlchemy()
cache = Cache()

def setup_logging(app):
    """
    Configure logging for the application
    """
    # Ensure logs directory exists
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure file handler with rotation
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'), 
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)

    # Configure app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    # Add console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    app.logger.addHandler(console_handler)

def create_app():
    # Create Flask app
    app = Flask(__name__)
    
    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/dbserial'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 20,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'max_overflow': 10,
        'pool_timeout': 30
    }
    
    # Caching Configuration
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    # Logging Setup
    setup_logging(app)

    # CORS Configuration
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Content-Type", 
                "Authorization", 
                "X-Requested-With",
                "Accept",
                "Cache-Control"
            ],
            "supports_credentials": True
        }
    })

    # Optional: Add error handlers
    @app.errorhandler(404)
    def not_found(error):
        app.logger.error(f'Not Found: {error}')
        return {'error': 'Not Found'}, 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(f'Server Error: {error}')
        return {'error': 'Internal Server Error'}, 500

    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    # Register blueprints
    from app.routes import sensor_routes, data_routes, report_routes
    app.register_blueprint(sensor_routes.bp)
    app.register_blueprint(data_routes.bp)
    app.register_blueprint(report_routes.bp)

    # Log app initialization
    app.logger.info('Application initialized successfully')

    return app