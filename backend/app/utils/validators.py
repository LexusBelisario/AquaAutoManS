from functools import wraps
from flask import request, jsonify
from datetime import datetime

class RequestValidator:
    @staticmethod
    def validate_sensor_data(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.json
            required_fields = ['temperature', 'oxygen', 'phlevel', 'turbidity']
            
            if not all(field in data for field in required_fields):
                return jsonify({
                    'error': 'Missing required fields',
                    'required_fields': required_fields
                }), 400
                
            # Validate data ranges
            if not (0 <= data['temperature'] <= 50):
                return jsonify({'error': 'Temperature out of valid range (0-50°C)'}), 400
                
            if not (0 <= data['oxygen'] <= 20):
                return jsonify({'error': 'Oxygen level out of valid range (0-20 mg/L)'}), 400
                
            if not (0 <= data['phlevel'] <= 14):
                return jsonify({'error': 'pH level out of valid range (0-14)'}), 400
                
            if not (0 <= data['turbidity'] <= 1000):
                return jsonify({'error': 'Turbidity out of valid range (0-1000 NTU)'}), 400
                
            return f(*args, **kwargs)
        return decorated_function

