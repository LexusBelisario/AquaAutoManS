from flask import Blueprint, jsonify, request
from app.services.report_service import ReportService
from app import cache

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
    time_filter = request.args.get('hours', default=0, type=int)
    date_filter = request.args.get('date', default=None, type=str)
    return report_service.print_data_report(time_filter, date_filter)