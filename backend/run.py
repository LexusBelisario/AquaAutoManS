from flask import Flask, jsonify
from flask_socketio import SocketIO
from app import create_app
from app.models import aquamans
from app.utils.error_handlers import ErrorHandler
from app.utils.custom_logger import CustomLogger
from app.utils.middleware import Middleware
from app.utils.system_monitor import SystemHealthCheck
import logging
import threading
import time

logging.basicConfig(level=logging.DEBUG)

app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")

ErrorHandler.init_app(app)
CustomLogger.setup_logger(app)
Middleware.track_requests(app)
system_monitor = SystemHealthCheck()

def broadcast_sensor_data():
    while True:
        try:
            with app.app_context():
                latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
                
                if latest_record:
                    data = {
                        'temperature': latest_record.temperature,
                        'oxygen': latest_record.oxygen,
                        'phlevel': latest_record.phlevel,
                        'turbidity': latest_record.turbidity,
                        'catfish': latest_record.catfish,
                        'dead_catfish': latest_record.dead_catfish,
                        'timestamp': latest_record.timeData.isoformat()
                    }
                    socketio.emit('sensor_update', data)
                    logging.info(f"Broadcasting sensor data: {data}")
        except Exception as e:
            logging.error(f"Error broadcasting sensor data: {e}")
        
        time.sleep(1) 
broadcast_thread = threading.Thread(target=broadcast_sensor_data, daemon=True)
broadcast_thread.start()

@app.route('/health')
def health_check():
    return jsonify(system_monitor.get_health_status())

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)