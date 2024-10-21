from flask import Flask, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
from datetime import datetime, timedelta
import cv2
from ultralytics import YOLO
import threading
import logging
import time

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/dbserial'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class aquamans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    oxygen = db.Column(db.Float)
    phlevel = db.Column(db.Float)
    turbidity = db.Column(db.Float)
    catfish = db.Column(db.Float, default=0)
    dead_catfish = db.Column(db.Float, default=0)
    timeData = db.Column(db.DateTime, default=datetime.utcnow)



@app.route('/temperature', methods=['GET'])
def get_temperature():
    try:
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            return jsonify({'temperature': latest_record.temperature})
        else:
            return jsonify({'temperature': 'N/A'})
    except Exception as e:
        print(f"Error fetching temperature: {e}")
        return jsonify({'error': str(e)})

@app.route('/oxygen', methods=['GET'])
def get_oxygen():
    try:
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            return jsonify({'oxygen': latest_record.oxygen})
        else:
            return jsonify({'oxygen': 'N/A'})
    except Exception as e:
        print(f"Error fetching oxygen: {e}")
        return jsonify({'error': str(e)})

@app.route('/phlevel', methods=['GET'])
def get_phlevel():
    try:
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            return jsonify({'phlevel': latest_record.phlevel})
        else:
            return jsonify({'phlevel': 'N/A'})
    except Exception as e:
        print(f"Error fetching phlevel: {e}")
        return jsonify({'error': str(e)})

@app.route('/turbidity', methods=['GET'])
def get_turbidity():
    try:
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            return jsonify({'turbidity': latest_record.turbidity})
        else:
            return jsonify({'turbidity': 'N/A'})
    except Exception as e:
        print(f"Error fetching turbidity: {e}")
        return jsonify({'error': str(e)})

@app.route('/data', methods=['GET'])
def get_data():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM aquamans"))
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]
            return jsonify(records)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({'error': str(e)})

@app.route('/temperature-data', methods=['GET'])
def get_temperature_data():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT id, temperature, timeData AS date FROM aquamans"))
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]
            return jsonify(records)
    except Exception as e:
        print(f"Error fetching temperature data: {e}")
        return jsonify({'error': str(e)})

@app.route('/weekly-temperature-data', methods=['GET'])
def get_weekly_temperature_data():
    try:
        # Get the filter type from query parameters (default is 'weekly')
        filter_type = request.args.get('filter', 'weekly')
        
        today = datetime.utcnow()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        with db.engine.connect() as connection:
            query = text("""
                SELECT temperature, timeData
                FROM aquamans
                WHERE timeData >= :start_date AND timeData <= :end_date
            """)
            result = connection.execute(query, {'start_date': start_of_week, 'end_date': end_of_week})
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]

            if filter_type == '3hours':
                # Filter the data to show every 3 hours
                filtered_records = []
                for record in records:
                    time_data = record['timeData']
                    hour = time_data.hour
                    if hour % 3 == 0:  # Select data points at 3-hour intervals
                        filtered_records.append(record)
                return jsonify(filtered_records)
            else:
                # Default to weekly data
                return jsonify(records)
    except Exception as e:
        print(f"Error fetching weekly temperature data: {e}")
        return jsonify({'error': str(e)})
    
@app.route('/weekly-oxygen-data', methods=['GET'])
def get_weekly_oxygen_data():
    try:
        # Get the filter type from query parameters (default is 'weekly')
        filter_type = request.args.get('filter', 'weekly')

        today = datetime.utcnow()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        with db.engine.connect() as connection:
            query = text("""
                SELECT oxygen, timeData
                FROM aquamans
                WHERE timeData >= :start_date AND timeData <= :end_date
            """)
            result = connection.execute(query, {'start_date': start_of_week, 'end_date': end_of_week})
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]

            if filter_type == '3hours':
                # Filter the data to show every 3 hours
                filtered_records = []
                for record in records:
                    time_data = record['timeData']
                    hour = time_data.hour
                    if hour % 3 == 0:  # Select data points at 3-hour intervals
                        filtered_records.append(record)
                return jsonify(filtered_records)
            else:
                # Default to weekly data
                return jsonify(records)
    except Exception as e:
        print(f"Error fetching weekly oxygen data: {e}")
        return jsonify({'error': str(e)})


@app.route('/weekly-ph-data', methods=['GET'])
def get_weekly_phlevel_data():
    try:
        # Get the filter type from query parameters (default is 'weekly')
        filter_type = request.args.get('filter', 'weekly')

        today = datetime.utcnow()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        with db.engine.connect() as connection:
            query = text("""
                SELECT phlevel, timeData
                FROM aquamans
                WHERE timeData >= :start_date AND timeData <= :end_date
            """)
            result = connection.execute(query, {'start_date': start_of_week, 'end_date': end_of_week})
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]

            if filter_type == '3hours':
                # Filter the data to show every 3 hours
                filtered_records = []
                for record in records:
                    time_data = record['timeData']
                    hour = time_data.hour
                    if hour % 3 == 0:  # Select data points at 3-hour intervals
                        filtered_records.append(record)
                return jsonify(filtered_records)
            else:
                # Default to weekly data
                return jsonify(records)
    except Exception as e:
        print(f"Error fetching weekly oxygen data: {e}")
        return jsonify({'error': str(e)})
    

if __name__ == "__main__":
    app.run(debug=True)
    
modelll = YOLO('C:/Users/user/AquaAutoManS/machine_learning/weights/best.pt')

frame_queue = []
sensor_data = {}

def read_frames(camera):
    while True:
        success, frame = camera.read()
        if not success:
            break
        frame = cv2.resize(frame, (640, 480))
        frame_queue.append(frame)
        
@app.route('/update_sensor_data', methods=['POST'])
def update_sensor_data():
    global sensor_data
    data = request.json
    sensor_data = {
        'temperature': data.get('temperature'),
        'oxygen': data.get('oxygen'),
        'phlevel': data.get('phlevel'),
        'turbidity': data.get('turbidity')
    }
    logging.debug(f"Updated sensor data: {sensor_data}")
    return jsonify({'status': 'success'})


@app.route('/camera_feed', methods=['GET'])
def camera_feed():
    # Try to initialize the Raspberry Pi camera
    try:
        pi_camera = cv2.VideoCapture(0)  # Replace with appropriate ID for the Pi camera
        if pi_camera.isOpened():
            return Response(generate_frames(pi_camera), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print("Error opening Raspberry Pi camera:", e)

    # If Pi camera fails, try to initialize the IP camera
    camera_url = 'http://192.168.18.137:8080/video'
    ip_camera = cv2.VideoCapture(camera_url)

    if not ip_camera.isOpened():
        return jsonify({'error': 'No cameras available'}), 404

    return Response(generate_frames(ip_camera), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames(camera):
    while True:
        success, frame = camera.read()
        if not success:
            break
        frame = cv2.resize(frame, (640, 480))  # Adjust frame size as needed
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def generate_frames():
    camera_url = 'http://192.168.18.137:8080/video'
    camera = cv2.VideoCapture(camera_url)

    if not camera.isOpened():
        print("Error: Could not open IP camera.")
        return

    fps = 30
    frame_interval = 3 / fps
    last_detection_time = time.time()

    while True:
        start_time = time.time()
        
        success, frame = camera.read()
        if not success:
            break
        frame = cv2.resize(frame, (320, 320))
        
        current_time = time.time()
        elapsed_time = current_time - last_detection_time

        if elapsed_time >= 2.0:
            results = modelll(frame)

            catfish_count = 0
            dead_catfish_count = 0

            conf_threshold = 0.5
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        conf = box.conf[0]
                        if conf > conf_threshold:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            label = result.names[int(box.cls[0])]
                            text = f"{label}: {conf:.2f}"
                            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                            if label == 'catfish':
                                catfish_count += 1
                            elif label == 'dead_catfish':
                                dead_catfish_count += 1

            # Fetch latest sensor data if missing
            if all(value is None for value in sensor_data.values()):
                # Query latest sensor data if it hasn't been updated yet
                latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
                if latest_record:
                    sensor_data['temperature'] = latest_record.temperature
                    sensor_data['oxygen'] = latest_record.oxygen
                    sensor_data['phlevel'] = latest_record.phlevel
                    sensor_data['turbidity'] = latest_record.turbidity

            if all(value is not None for value in sensor_data.values()):
                try:
                    with app.app_context():
                        new_record = aquamans(
                            temperature=sensor_data.get('temperature'),
                            oxygen=sensor_data.get('oxygen'),
                            phlevel=sensor_data.get('phlevel'),
                            turbidity=sensor_data.get('turbidity'),
                            catfish=catfish_count,
                            dead_catfish=dead_catfish_count,
                            timeData=datetime.utcnow()
                        )
                        db.session.add(new_record)
                        db.session.commit()
                except Exception as e:
                    logging.error(f"Error updating data: {e}")

            last_detection_time = current_time
        
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # Ensure we process at least 10 fps
        processing_time = time.time() - start_time
        if processing_time < frame_interval:
            time.sleep(frame_interval - processing_time)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/catfish', methods=['GET'])
def get_catfish():
    try:
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            return jsonify({'catfish': latest_record.catfish, 'dead_catfish': latest_record.dead_catfish})
        else:
            return jsonify({'catfish': 'N/A', 'dead_catfish': 'N/A'})
    except Exception as e:
        print(f"Error fetching catfish data: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)