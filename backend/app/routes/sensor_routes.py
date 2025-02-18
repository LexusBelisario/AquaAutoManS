from flask import Blueprint, jsonify, request
from app.services.sensor_service import SensorService
from app import cache, db
from app.models import aquamans
from app.utils.limiters import limiter
import logging

bp = Blueprint('sensor', __name__)
sensor_service = SensorService()

@bp.route('/temperature', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=60)
def get_temperature():
    return sensor_service.get_temperature()

@bp.route('/oxygen', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=60)
def get_oxygen():
    return sensor_service.get_oxygen()

@bp.route('/phlevel', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=60)
def get_phlevel():
    return sensor_service.get_phlevel()

@bp.route('/turbidity', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=60)
def get_turbidity():
    return sensor_service.get_turbidity()

@bp.route('/update_sensor_data', methods=['POST'])
@limiter.limit("100/minute")
def update_sensor_data():
    return sensor_service.update_sensor_data(request.json)

@bp.route('/update_detection', methods=['POST'])
@limiter.exempt
def update_detection():
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        catfish_count = int(data.get('catfish', 0))
        dead_catfish_count = int(data.get('dead_catfish', 0))
        
        # Get the latest record
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        
        if latest_record:
            latest_record.catfish = catfish_count
            latest_record.dead_catfish = dead_catfish_count
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Detection data updated',
                'data': {
                    'catfish': catfish_count,
                    'dead_catfish': dead_catfish_count
                }
            })
        else:
            return jsonify({'status': 'error', 'message': 'No record found to update'}), 404

    except Exception as e:
        logging.error(f"Error updating detection data: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/catfish', methods=['GET'])
@limiter.exempt
def get_catfish():
    try:
        latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
        if latest_record:
            return jsonify({
                'status': 'success',
                'catfish': latest_record.catfish
            })
        return jsonify({
            'status': 'error',
            'catfish': 0
        })
    except Exception as e:
        logging.error(f"Error fetching catfish count: {e}")
        return jsonify({
            'status': 'error',
            'catfish': 0
        })

@bp.route('/dead_catfish', methods=['GET'])
@limiter.exempt
def get_dead_catfish():
    try:
        latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
        if latest_record:
            return jsonify({
                'status': 'success',
                'dead_catfish': latest_record.dead_catfish
            })
        return jsonify({
            'status': 'error',
            'dead_catfish': 0
        })
    except Exception as e:
        logging.error(f"Error fetching dead catfish count: {e}")
        return jsonify({
            'status': 'error',
            'dead_catfish': 0
        })