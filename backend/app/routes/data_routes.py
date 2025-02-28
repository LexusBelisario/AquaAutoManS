from flask import Blueprint, jsonify, request
from app import cache, db  # Import db here
from app.services.data_service import DataService
from app.utils.limiters import limiter
from app.models import aquamans
from datetime import datetime, timedelta
import logging
bp = Blueprint('data', __name__)
data_service = DataService()

bp = Blueprint('data', __name__)
data_service = DataService()

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
@cache.cached(timeout=300, query_string=True)  # Cache for 5 minutes
def get_filtered_temperature_data():
    filter_type = request.args.get('filter', 'weekly')
    if filter_type not in ['weekly', '3hours', 'date', 'week']:
        return jsonify({
            'error': 'Invalid filter type'
        }), 400
    
    try:
        query = db.session.query(aquamans)

        if filter_type == '3hours':
            time_threshold = datetime.utcnow() - timedelta(hours=24)
            query = query.filter(aquamans.timeData >= time_threshold)
        
        elif filter_type == 'date':
            selected_date = request.args.get('selected_date')
            if selected_date:
                date = datetime.strptime(selected_date, '%Y-%m-%d')
                next_date = date + timedelta(days=1)
                query = query.filter(
                    aquamans.timeData >= date,
                    aquamans.timeData < next_date
                )
        
        elif filter_type == 'week':
            week_start = request.args.get('week_start')
            if week_start:
                start_date = datetime.strptime(week_start, '%Y-%m-%d')
                end_date = start_date + timedelta(days=7)
                query = query.filter(
                    aquamans.timeData >= start_date,
                    aquamans.timeData < end_date
                )
        
        else:  # weekly (default)
            time_threshold = datetime.utcnow() - timedelta(days=7)
            query = query.filter(aquamans.timeData >= time_threshold)

        # Add index hint and limit results
        results = query.order_by(aquamans.timeData.asc()).limit(1000).all()
        
        data = [{
            'timeData': record.timeData.strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': record.temperature
        } for record in results]

        return jsonify(data)

    except Exception as e:
        logging.error(f"Error in filtered temperature data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/oxygen-data', methods=['GET'])
@limiter.exempt
def get_oxygen_data():
    return data_service.get_oxygen_data()

@bp.route('/filtered-oxygen-data', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=300, query_string=True)  # Cache for 5 minutes
def get_filtered_oxygen_data():
    filter_type = request.args.get('filter', 'weekly')
    if filter_type not in ['weekly', '3hours', 'date', 'week']:
        return jsonify({
            'error': 'Invalid filter type'
        }), 400
    
    try:
        query = db.session.query(aquamans)

        if filter_type == '3hours':
            time_threshold = datetime.utcnow() - timedelta(hours=24)
            query = query.filter(aquamans.timeData >= time_threshold)
        
        elif filter_type == 'date':
            selected_date = request.args.get('selected_date')
            if selected_date:
                date = datetime.strptime(selected_date, '%Y-%m-%d')
                next_date = date + timedelta(days=1)
                query = query.filter(
                    aquamans.timeData >= date,
                    aquamans.timeData < next_date
                )
        
        elif filter_type == 'week':
            week_start = request.args.get('week_start')
            if week_start:
                start_date = datetime.strptime(week_start, '%Y-%m-%d')
                end_date = start_date + timedelta(days=7)
                query = query.filter(
                    aquamans.timeData >= start_date,
                    aquamans.timeData < end_date
                )
        
        else:  # weekly (default)
            time_threshold = datetime.utcnow() - timedelta(days=7)
            query = query.filter(aquamans.timeData >= time_threshold)

        # Add index hint and limit results
        results = query.order_by(aquamans.timeData.asc()).limit(1000).all()
        
        data = [{
            'timeData': record.timeData.strftime('%Y-%m-%d %H:%M:%S'),
            'oxygen': record.oxygen
        } for record in results]

        return jsonify(data)

    except Exception as e:
        logging.error(f"Error in filtered oxygen data: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
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

@bp.route('/api/latest-detection', methods=['GET'])
def get_latest_detection():
    try:
        # Query your database for the latest detection
        latest_data = db.session.query(aquamans).order_by(aquamans.id.desc()).first()
        
        return jsonify({
            'catfish': latest_data.catfish,
            'dead_catfish': latest_data.dead_catfish
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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