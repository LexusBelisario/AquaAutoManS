from flask import Blueprint, Response, jsonify
from app.utils.limiters import limiter
from flask_cors import CORS
import cv2
import logging
import time
from ultralytics import YOLO
from datetime import datetime, timedelta
import mysql.connector
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image
from io import BytesIO

video_bp = Blueprint('video', __name__)
CORS(video_bp)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_detect.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API and Database Configuration
FLASK_API_URL = "http://127.0.0.1:5000/update_detection"
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'dbserial'
}

# Configure requests with retry strategy
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Load YOLO model
try:
    model = YOLO("C:/Users/ADMIN/AquaAutoManS/machine_learning/weights/best1.pt")
    class_names = ["catfish", "dead_catfish"]
    logger.info("YOLO model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {str(e)}")
    model = None

# Global variables
camera = None
start_time = datetime.now()
last_capture_time = None
dead_catfish_detected = False

def get_db_connection():
    """Establish database connection with retry mechanism"""
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(**db_config)
            return connection
        except mysql.connector.Error as e:
            logger.error(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("All database connection attempts failed")
                return None

def get_latest_sensor_data():
    """Retrieve the latest sensor data from database"""
    try:
        connection = get_db_connection()
        if connection is None:
            return None
        
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM aquamans ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        latest_record = cursor.fetchone()
        cursor.close()
        connection.close()
        return latest_record
    except mysql.connector.Error as e:
        logger.error(f"Error fetching latest sensor data: {e}")
        return None

def send_detection_data(catfish_count, dead_catfish_count):
    """Send detection data to Flask API"""
    data = {
        'catfish': catfish_count,
        'dead_catfish': dead_catfish_count
    }
    try:
        response = session.post(
            FLASK_API_URL,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        response.raise_for_status()
        logger.info(f"Data sent successfully: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending data to Flask API: {e}")
        return False

def insert_data_to_db(data):
    """Insert new data into database"""
    try:
        connection = get_db_connection()
        if connection is None:
            return
        
        cursor = connection.cursor()
        query = """
        INSERT INTO aquamans (
            temperature, tempResult, oxygen, oxygenResult, 
            phlevel, phResult, turbidity, turbidityResult, 
            catfish, dead_catfish, timeData, dead_catfish_image
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, data)
        connection.commit()
        cursor.close()
        connection.close()
        logger.info("Successfully inserted data into database")
    except mysql.connector.Error as e:
        logger.error(f"Error uploading data to MySQL: {e}")

def init_camera():
    """Initialize and configure camera"""
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            logger.error("Failed to open camera")
            return None

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        return camera
    except Exception as e:
        logger.error(f"Camera initialization error: {str(e)}")
        return None

def process_frame(frame):
    """Process frame with YOLO detection"""
    try:
        if model is None:
            return frame, 0, 0

        results = model.predict(frame, conf=0.25, iou=0.5)
        catfish_count = 0
        dead_catfish_count = 0

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                if (x2 - x1) < 20 or (y2 - y1) < 20:
                    continue
                
                label = f"{class_names[cls]} {conf:.2f}"
                color = (0, 255, 0) if cls == 0 else (0, 0, 255)
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                if cls == 0:
                    catfish_count += 1
                elif cls == 1:
                    dead_catfish_count += 1

        return frame, catfish_count, dead_catfish_count

    except Exception as e:
        logger.error(f"Error in process_frame: {str(e)}")
        return frame, 0, 0

def generate_frames():
    """Generate video frames with detection"""
    global camera, start_time, last_capture_time, dead_catfish_detected
    
    if camera is None:
        camera = init_camera()
        if camera is None:
            return

    try:
        while True:
            # Check for hourly rest period
            elapsed_time = datetime.now() - start_time
            if elapsed_time >= timedelta(hours=1):
                logger.info("Resting for 5 minutes to prevent overheating...")
                time.sleep(300)
                start_time = datetime.now()
                continue

            # Capture frame
            ret, frame = camera.read()
            if not ret:
                logger.error("Failed to capture frame")
                time.sleep(1)
                continue

            # Process frame with detection
            frame, catfish_count, dead_catfish_count = process_frame(frame)

            # Send detection data to API
            if catfish_count > 0 or dead_catfish_count > 0:
                if send_detection_data(catfish_count, dead_catfish_count):
                    logger.info(f"Detection data sent - Catfish: {catfish_count}, Dead: {dead_catfish_count}")
                else:
                    logger.warning("Failed to send detection data")

            # Handle dead catfish detection
            if dead_catfish_count > 0:
                dead_catfish_detected = True
                current_time = datetime.now()
                
                if last_capture_time is None or \
                   (current_time - last_capture_time).total_seconds() >= 20:
                    try:
                        last_capture_time = current_time
                        
                        # Convert frame to JPEG
                        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        img_byte_arr = BytesIO()
                        pil_image.save(img_byte_arr, format='JPEG')
                        img_byte_arr = img_byte_arr.getvalue()

                        # Get and update sensor data
                        latest_data = get_latest_sensor_data()
                        if latest_data:
                            data_to_insert = (
                                latest_data["temperature"],
                                latest_data["tempResult"],
                                latest_data["oxygen"],
                                latest_data["oxygenResult"],
                                latest_data["phlevel"],
                                latest_data["phResult"],
                                latest_data["turbidity"],
                                latest_data["turbidityResult"],
                                catfish_count,
                                dead_catfish_count,
                                current_time,
                                img_byte_arr
                            )
                            insert_data_to_db(data_to_insert)
                            logger.info("Database updated with new detection data")
                    except Exception as e:
                        logger.error(f"Error handling dead catfish detection: {e}")

            # Add timestamp and counts to frame
            cv2.putText(frame, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Live Catfish: {catfish_count}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Dead Catfish: {dead_catfish_count}", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Encode and yield frame
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    except Exception as e:
        logger.error(f"Error in generate_frames: {str(e)}")
    finally:
        if camera is not None:
            camera.release()

@video_bp.route('/video_feed')
@limiter.exempt
def video_feed():
    """Video streaming route"""
    try:
        return Response(
            generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame',
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'Access-Control-Allow-Origin': '*'
            }
        )
    except Exception as e:
        logger.error(f"Video feed error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@video_bp.route('/detection_status')
def detection_status():
    """Get current detection status"""
    try:
        latest_record = get_latest_sensor_data()
        return jsonify({
            'status': 'success',
            'catfish_count': latest_record["catfish"] if latest_record else 0,
            'dead_catfish_count': latest_record["dead_catfish"] if latest_record else 0,
            'last_update': latest_record["timeData"].isoformat() if latest_record else None
        })
    except Exception as e:
        logger.error(f"Error getting detection status: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@video_bp.route('/system_status')
def system_status():
    """Get system rest status"""
    try:
        global start_time
        elapsed_time = datetime.now() - start_time
        is_resting = elapsed_time >= timedelta(hours=1)
        
        return jsonify({
            'status': 'success',
            'is_resting': is_resting,
            'message': "System is resting for 5 minutes to prevent overheating" if is_resting else "System is active",
            'next_rest': (timedelta(hours=1) - elapsed_time).total_seconds() if not is_resting else 300  # Time until next rest or remaining rest time
        })
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return jsonify({'error': str(e)}), 500