from flask import Flask, jsonify
from flask_compress import Compress
from app import create_app
from app.utils.error_handlers import ErrorHandler
from app.utils.custom_logger import CustomLogger
from app.utils.middleware import Middleware
from app.utils.system_monitor import SystemHealthCheck
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = create_app()

# Initialize extensions
compress = Compress(app)

# Initialize error handlers
ErrorHandler.init_app(app)

# Setup custom logging
CustomLogger.setup_logger(app)

# Apply middleware
Middleware.track_requests(app)

# System monitor
system_monitor = SystemHealthCheck()

@app.route('/health')
def health_check():
    return jsonify(system_monitor.get_health_status())  # Changed from system_health to system_monitor

if __name__ == '__main__':
    app.run(debug=True, threaded=True)