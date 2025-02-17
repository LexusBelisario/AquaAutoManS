# app/services/sensor_service.py
from flask import jsonify
from app.models import aquamans
from app import db
from datetime import datetime
import logging

class SensorService:
    def get_temperature(self):
        try:
            latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
            if latest_record:
                logging.debug(f"Latest temperature record: {latest_record.temperature}")
                return jsonify({'temperature': latest_record.temperature})
            return jsonify({'temperature': 'N/A'})
        except Exception as e:
            logging.error(f"Error fetching temperature: {e}")
            return jsonify({'error': str(e)})

    def get_oxygen(self):
        try:
            latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
            if latest_record:
                logging.debug(f"Latest oxygen record: {latest_record.oxygen}")
                return jsonify({'oxygen': latest_record.oxygen})
            return jsonify({'oxygen': 'N/A'})
        except Exception as e:
            logging.error(f"Error fetching oxygen: {e}")
            return jsonify({'error': str(e)})

    def get_phlevel(self):
        try:
            latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
            if latest_record:
                logging.debug(f"Latest pH level record: {latest_record.phlevel}")
                return jsonify({'phlevel': latest_record.phlevel})
            return jsonify({'phlevel': 'N/A'})
        except Exception as e:
            logging.error(f"Error fetching pH level: {e}")
            return jsonify({'error': str(e)})

    def get_turbidity(self):
        try:
            latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
            if latest_record:
                logging.debug(f"Latest turbidity record: {latest_record.turbidity}")
                return jsonify({'turbidity': latest_record.turbidity})
            return jsonify({'turbidity': 'N/A'})
        except Exception as e:
            logging.error(f"Error fetching turbidity: {e}")
            return jsonify({'error': str(e)})

    def update_sensor_data(self, data):
        try:
            new_record = aquamans(
                temperature=data.get('temperature'),
                oxygen=data.get('oxygen'),
                phlevel=data.get('phlevel'),
                turbidity=data.get('turbidity'),
                timeData=datetime.utcnow()
            )
            db.session.add(new_record)
            db.session.commit()
            logging.debug(f"Updated sensor data: {new_record}")
            return jsonify({'status': 'success'})
        except Exception as e:
            logging.error(f"Error updating sensor data: {e}")
            return jsonify({'status': 'failure', 'error': str(e)})

    def update_detection(self, data):
        try:
            catfish_count = int(data.get('catfish', 0))
            dead_catfish_count = int(data.get('dead_catfish', 0))

            latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
            if latest_record:
                latest_record.catfish = catfish_count
                latest_record.dead_catfish = dead_catfish_count
                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Detection data updated'})
            return jsonify({'status': 'failure', 'message': 'No record to update'})
        except Exception as e:
            logging.error(f"Error updating detection data: {e}")
            return jsonify({'status': 'error', 'message': str(e)})