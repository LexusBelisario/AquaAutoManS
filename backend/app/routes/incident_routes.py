from flask import Blueprint, jsonify, send_file
from app.services.incident_service import IncidentService
import logging

bp = Blueprint('incident', __name__, url_prefix='/api')
incident_service = IncidentService()

@bp.route('/incident-report', methods=['GET'])
def get_incident_report():
    """Get incident report endpoint"""
    try:
        logging.info(f"Received incident report request at {incident_service.current_timestamp}")
        report = incident_service.generate_incident_report()
        
        if report.get("error"):
            return jsonify(report), 500
        return jsonify(report)
    except Exception as e:
        logging.error(f"Route error in get_incident_report: {str(e)}")
        return jsonify({
            "error": True,
            "message": str(e),
            "timestamp": "2025-03-21 12:40:03",
            "reported_by": "LexusBelisario"
        }), 500

@bp.route('/incident-report/<incident_id>/pdf', methods=['GET'])
def download_pdf_report(incident_id):
    """Download PDF report endpoint"""
    try:
        logging.info(f"Received PDF report request for incident {incident_id}")
        report_data = incident_service.generate_incident_report()
        
        if report_data.get("error"):
            return jsonify(report_data), 500

        pdf_buffer = incident_service.generate_pdf_report(report_data, incident_id)
        
        return send_file(
            pdf_buffer,
            download_name=f'water-quality-report-{incident_id}.pdf',
            mimetype='application/pdf',
            as_attachment=True
        )
    except Exception as e:
        logging.error(f"Route error in download_pdf_report: {str(e)}")
        return jsonify({
            "error": True,
            "message": str(e),
            "timestamp": "2025-03-21 12:40:03",
            "reported_by": "LexusBelisario"
        }), 500