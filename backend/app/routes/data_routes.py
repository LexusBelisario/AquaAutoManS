from flask import Blueprint, jsonify, request, send_file, current_app
from flask_cors import cross_origin
from app.services.data_service import DataService
from app import cache
from app.utils.limiters import limiter
from datetime import datetime
import logging
import traceback
import pandas as pd
import io

bp = Blueprint('data', __name__)
data_service = DataService()

@bp.route('/check_data/print', methods=['GET'])
@limiter.exempt
@cross_origin(supports_credentials=True)
def generate_report():
    try:
        # Extract parameters
        date_filter = request.args.get('date')
        hours_filter = request.args.get('hours')

        # Logging
        current_app.logger.info(f"Report generation request - Date: {date_filter}, Hours: {hours_filter}")

        # Validate date or hours filter
        if not date_filter and not hours_filter:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Provide either date or hours filter'
            }), 400

        # Fetch data based on filters
        with db.engine.connect() as connection:
            if date_filter:
                # Parse date
                try:
                    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({
                        'error': 'Invalid date format',
                        'message': 'Use YYYY-MM-DD format'
                    }), 400

                # Query for specific date
                query = """
                    SELECT * FROM aquamans 
                    WHERE DATE(timeData) = :filter_date 
                    ORDER BY timeData
                """
                result = connection.execute(text(query), {'filter_date': filter_date})

            elif hours_filter:
                # Parse hours
                hours = int(hours_filter)
                
                # Query for recent hours
                query = """
                    SELECT * FROM aquamans 
                    WHERE timeData >= NOW() - INTERVAL :hours HOUR 
                    ORDER BY timeData
                """
                result = connection.execute(text(query), {'hours': hours})

            # Convert to DataFrame
            columns = result.keys()
            df = pd.DataFrame([dict(zip(columns, row)) for row in result])

            # Perform aggregations
            aggregations = {
                'Total Temperature': df['temperature'].mean(),
                'Temperature Min': df['temperature'].min(),
                'Temperature Max': df['temperature'].max(),
                'Total Oxygen': df['oxygen'].mean(),
                'Oxygen Min': df['oxygen'].min(),
                'Oxygen Max': df['oxygen'].max(),
                'Total pH Level': df['phlevel'].mean(),
                'pH Min': df['phlevel'].min(),
                'pH Max': df['phlevel'].max(),
                'Total Turbidity': df['turbidity'].mean(),
                'Turbidity Min': df['turbidity'].min(),
                'Turbidity Max': df['turbidity'].max(),
                'Total Alive Catfish': df['catfish'].sum(),
                'Total Dead Catfish': df['dead_catfish'].sum()
            }

            # Create summary DataFrame
            summary_df = pd.DataFrame.from_dict(
                aggregations, 
                orient='index', 
                columns=['Value']
            )

            # Prepare Excel file
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Raw data sheet
                df.to_excel(writer, sheet_name='Raw Data', index=False)
                
                # Summary sheet
                summary_df.to_excel(writer, sheet_name='Summary')

            output.seek(0)

            # Send file
            return send_file(
                output, 
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True, 
                download_name=f'data_report_{date_filter or f"{hours_filter}_hours"}.xlsx'
            )

    except Exception as e:
        current_app.logger.error(f"Error generating report: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        
        return jsonify({
            'error': 'Report generation failed',
            'message': str(e)
        }), 500
        
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