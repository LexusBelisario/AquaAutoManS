from flask import jsonify
import logging
from datetime import datetime
import traceback

class ErrorHandler:
    @staticmethod
    def init_app(app):
        @app.errorhandler(400)
        def bad_request_error(error):
            return ErrorHandler._handle_error(error, 400)

        @app.errorhandler(404)
        def not_found_error(error):
            return ErrorHandler._handle_error(error, 404)

        @app.errorhandler(500)
        def internal_error(error):
            return ErrorHandler._handle_error(error, 500)

        @app.errorhandler(Exception)
        def handle_exception(error):
            return ErrorHandler._handle_error(error, 500)

    @staticmethod
    def _handle_error(error, status_code):
        error_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': status_code,
            'error': str(error),
            'trace_id': datetime.utcnow().timestamp()
        }
        
        if status_code == 500:
            error_data['stack_trace'] = traceback.format_exc()
            
        logging.error(f"Error {status_code}: {error_data}")
        return jsonify(error_data), status_code