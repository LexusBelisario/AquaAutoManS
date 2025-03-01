from flask import Blueprint, jsonify, request
from app.extensions import db
from app.services.water_quality_service import WaterQualityService
from app.models import aquamans
from datetime import datetime, timedelta

bp = Blueprint('water_quality', __name__, url_prefix='/api/water-quality')
water_quality_service = WaterQualityService()

@bp.route('/check', methods=['GET'])
def check_water_quality():
    try:
        # Get latest record
        latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
        if not latest_record:
            return jsonify({"message": "No data available"})

        # Get historical data for trend analysis
        three_hours_ago = latest_record.timeData - timedelta(hours=3)
        historical_data = (
            aquamans.query
            .filter(aquamans.timeData >= three_hours_ago)
            .order_by(aquamans.timeData)
            .all()
        )

        # Calculate trends
        temperature_trend = calculate_trend([record.temperature for record in historical_data])
        oxygen_trend = calculate_trend([record.oxygen for record in historical_data])
        ph_trend = calculate_trend([record.phlevel for record in historical_data])
        turbidity_trend = calculate_trend([record.turbidity for record in historical_data])

        return jsonify({
            "alert_id": f"wq_{latest_record.id}",
            "time_detected": latest_record.timeData.isoformat(),
            "temperature": latest_record.temperature,
            "tempResult": latest_record.tempResult,
            "temperature_trend": temperature_trend,
            "oxygen": latest_record.oxygen,
            "oxygenResult": latest_record.oxygenResult,
            "oxygen_trend": oxygen_trend,
            "phlevel": latest_record.phlevel,
            "phResult": latest_record.phResult,
            "ph_trend": ph_trend,
            "turbidity": latest_record.turbidity,
            "turbidityResult": latest_record.turbidityResult,
            "turbidity_trend": turbidity_trend,
            "historical_data": {
                "temperature": format_historical_data(historical_data, 'temperature'),
                "oxygen": format_historical_data(historical_data, 'oxygen'),
                "ph": format_historical_data(historical_data, 'phlevel'),
                "turbidity": format_historical_data(historical_data, 'turbidity')
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def calculate_trend(values):
    if len(values) < 2:
        return "→"
    
    last_values = values[-5:] if len(values) > 5 else values
    first = sum(last_values[:len(last_values)//2]) / (len(last_values)//2)
    second = sum(last_values[len(last_values)//2:]) / (len(last_values) - len(last_values)//2)
    
    if abs(second - first) < 0.1:
        return "→"
    return "↑" if second > first else "↓"

def format_historical_data(records, parameter):
    return {
        'labels': [record.timeData.strftime("%H:%M") for record in records],
        'datasets': [{
            'label': parameter.title(),
            'data': [getattr(record, parameter) for record in records],
            'borderColor': 'rgb(75, 192, 192)',
            'tension': 0.1
        }]
    }

@bp.route('/print/<alert_id>', methods=['GET'])
def print_water_quality_report(alert_id):
    return water_quality_service.print_water_quality_report(alert_id)

@bp.route('/trends', methods=['GET'])
def get_water_quality_trends():
    hours = request.args.get('hours', default=24, type=int)
    return water_quality_service.get_trends(hours)

@bp.route('/predictions', methods=['GET'])
def get_water_quality_predictions():
    hours_ahead = request.args.get('hours_ahead', default=6, type=int)
    return water_quality_service.get_predictions(hours_ahead)

@bp.route('/correlations', methods=['GET'])
def get_parameter_correlations():
    return water_quality_service.get_parameter_correlations()