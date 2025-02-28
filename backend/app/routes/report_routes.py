from flask import Blueprint, jsonify, request, Response
from app.services.report_service import ReportService
from app import cache
from datetime import datetime

bp = Blueprint('report', __name__)
report_service = ReportService()

@bp.route('/check_dead_catfish', methods=['GET'])
def check_dead_catfish():
    return report_service.check_dead_catfish()

@bp.route('/check_dead_catfish/print/<alert_id>', methods=['GET'])
def print_dead_catfish_report(alert_id):
    return report_service.print_dead_catfish_report(alert_id)

@bp.route('/check_data/print', methods=['GET'])
def print_data_report():
    try:
        time_filter = request.args.get('hours', default=0, type=int)
        date_filter = request.args.get('date', default=None, type=str)

        # Validate date format if provided
        if date_filter:
            try:
                datetime.strptime(date_filter, "%Y-%m-%d")
            except ValueError:
                return jsonify({
                    "error": "Invalid date format. Please use YYYY-MM-DD"
                }), 400

        # Validate hours if provided
        if time_filter < 0:
            return jsonify({
                "error": "Hours filter must be a positive number"
            }), 400

        return report_service.print_data_report(time_filter, date_filter)

    except Exception as e:
        return jsonify({
            "error": "An error occurred while generating the report",
            "details": str(e)
        }), 500

# Add error handlers for the blueprint
@bp.errorhandler(404)
def handle_404(e):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@bp.errorhandler(500)
def handle_500(e):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500