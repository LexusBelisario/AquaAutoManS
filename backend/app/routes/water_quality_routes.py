# app/routes/water_quality_routes.py
from flask import Blueprint, jsonify, request
from app.services.water_quality_service import WaterQualityService
from app import cache

bp = Blueprint('water_quality', __name__)
water_quality_service = WaterQualityService()

@bp.route('/check_water_quality', methods=['GET'])
def check_water_quality():
    return water_quality_service.check_water_quality()

@bp.route('/check_water_quality/print/<alert_id>', methods=['GET'])
def print_water_quality_report(alert_id):
    return water_quality_service.print_water_quality_report(alert_id)

@bp.route('/water_quality/trends', methods=['GET'])
def get_water_quality_trends():
    hours = request.args.get('hours', default=24, type=int)
    return water_quality_service.get_trends(hours)

@bp.route('/water_quality/predictions', methods=['GET'])
def get_water_quality_predictions():
    hours_ahead = request.args.get('hours_ahead', default=6, type=int)
    return water_quality_service.get_predictions(hours_ahead)

@bp.route('/water_quality/correlations', methods=['GET'])
def get_parameter_correlations():
    return water_quality_service.get_parameter_correlations()