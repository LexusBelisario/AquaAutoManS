from flask import request, g, current_app
import time
from functools import wraps
from datetime import datetime

class Middleware:
    @staticmethod
    def request_timer(app):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                start_time = time.time()
                response = f(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log request duration using the passed app instance
                app.logger.info(f'Request to {request.path} took {duration:.2f} seconds')
                
                return response
            return decorated_function
        return decorator

    @staticmethod
    def track_requests(app):
        @app.before_request
        def before_request():
            g.start_time = time.time()
            g.request_id = datetime.utcnow().timestamp()

        @app.after_request
        def after_request(response):
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
                app.logger.info(f'Request {g.request_id} completed in {duration:.2f}s')
            return response