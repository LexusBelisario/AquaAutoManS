from flask import Blueprint, jsonify, request
from flask_caching import Cache
from app.services.data_service import DataService
from app import cache
from app.utils.limiters import limiter
from app.models import aquamans
from datetime import datetime, timedelta
import logging
bp = Blueprint('data', __name__)
data_service = DataService()

cache = Cache(config={'CACHE_TYPE': 'simple'})

@bp.route('/data', methods=['GET'])
@limiter.exempt
def get_data():
    date_filter = request.args.get('date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return data_service.get_data(date_filter, page, per_page)

@bp.route('/temperature-data', methods=['GET'])
@limiter.exempt
def get_temperature_data():
    return data_service.get_temperature_data()

@bp.route('/filtered-temperature-data', methods=['GET'])
@limiter.exempt
def get_filtered_temperature_data():
    filter_type = request.args.get('filter', 'date')
    selected_date = request.args.get('selected_date')
    selected_week_start = request.args.get('week_start')
    return data_service.get_filtered_temperature_data(filter_type, selected_date, selected_week_start)

@bp.route('/oxygen-data', methods=['GET'])
@limiter.exempt
def get_oxygen_data():
    return data_service.get_oxygen_data()

@bp.route('/filtered-oxygen-data', methods=['GET'])
@limiter.exempt
def get_filtered_oxygen_data():
    filter_type = request.args.get('filter', 'date')
    selected_date = request.args.get('selected_date')
    selected_week_start = request.args.get('week_start')
    return data_service.get_filtered_oxygen_data(filter_type, selected_date, selected_week_start)

@bp.route('/phlevel-data', methods=['GET'])
@limiter.exempt
def get_phlevel_data():
    return data_service.get_phlevel_data()

@bp.route('/filtered-phlevel-data', methods=['GET'])
@limiter.exempt
def get_filtered_phlevel_data():
    filter_type = request.args.get('filter', 'date')
    selected_date = request.args.get('selected_date')
    selected_week_start = request.args.get('week_start')
    return data_service.get_filtered_phlevel_data(filter_type, selected_date, selected_week_start)

@bp.route('/turbidity-data', methods=['GET'])
@limiter.exempt
def get_turbidity_data():
    return data_service.get_turbidity_data()

@bp.route('/filtered-turbidity-data', methods=['GET'])
@limiter.exempt
def get_filtered_turbidity_data():
    filter_type = request.args.get('filter', 'date')
    selected_date = request.args.get('selected_date')
    selected_week_start = request.args.get('week_start')
    return data_service.get_filtered_turbidity_data(filter_type, selected_date, selected_week_start)

# Add support for weekly filter
def handle_weekly_filter(query, week_start):
    """Helper function to handle weekly filtering"""
    if week_start:
        try:
            start_date = datetime.strptime(week_start, '%Y-%m-%d')
            end_date = start_date + timedelta(days=7)
            return query.filter(
                aquamans.timeData >= start_date,
                aquamans.timeData < end_date
            )
        except ValueError:
            return None
    return query

@bp.route('/weekly-data', methods=['GET'])
@limiter.exempt
def get_weekly_data():
    week_start = request.args.get('week_start')
    return data_service.get_weekly_data(week_start)

@bp.route('/latest-image', methods=['GET'])
@limiter.exempt
def get_latest_image():
    return data_service.get_latest_image()

# Error handler for this blueprint
@bp.errorhandler(404)
def handle_404(e):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'timestamp': datetime.utcnow().isoformat()
    }), 404

@bp.errorhandler(500)
def handle_500(e):
    logging.error(f"Internal server error: {str(e)}")
    return jsonify({
        'error': 'Internal server error',
        'message': str(e),
        'timestamp': datetime.utcnow().isoformat()
    }), 500