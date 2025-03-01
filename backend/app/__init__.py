# app/__init__.py
from flask import Flask, jsonify
from flask_cors import CORS
from app.extensions import db, cache, compress
from app.utils.limiters import limiter
from app.config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    compress.init_app(app)
    
    # Enable CORS
    CORS(app)

    # Test database connection
    with app.app_context():
        try:
            db.engine.connect()
            print("Database connection successful!")
            # Create all tables
            db.create_all()
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise

    # Register blueprints
    with app.app_context():
        from app.routes import sensor_routes, data_routes, report_routes, video_routes
        from app.routes.water_quality_routes import bp as water_quality_bp
        
        app.register_blueprint(sensor_routes.bp)
        app.register_blueprint(data_routes.bp)
        app.register_blueprint(report_routes.bp)
        app.register_blueprint(video_routes.video_bp, url_prefix='/video')
        app.register_blueprint(water_quality_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500

    return app