# app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from app.utils.limiters import limiter

# Initialize extensions
db = SQLAlchemy()
cache = Cache()

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/dbserial'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 20,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'max_overflow': 10,
        'pool_timeout': 30
    }
    
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize extensions with app
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    with app.app_context():
        # Import routes here to avoid circular imports
        from app.routes import sensor_routes, data_routes, report_routes, video_routes
        
        app.register_blueprint(sensor_routes.bp)
        app.register_blueprint(data_routes.bp)
        app.register_blueprint(report_routes.bp)
        app.register_blueprint(video_routes.video_bp, url_prefix='/video')

    return app