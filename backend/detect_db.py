import cv2
import requests
import base64
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
from datetime import datetime, timedelta
import mysql.connector
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('detect.log'),
        logging.StreamHandler()
    ]
)

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
model = YOLO("C:/Users/user/AquaAutoManS/machine_learning/weights/best1.pt")
class_names = ["catfish", "dead_catfish"]

# Initialize video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    logging.error("Error: Could not open webcam.")
    exit()

# Initialize detection variables
dead_catfish_detected = False
last_capture_time = None

def get_db_connection():
    """Establish database connection with retry mechanism"""
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(**db_config)
            return connection
        except mysql.connector.Error as e:
            logging.error(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logging.error("All database connection attempts failed")
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
        logging.error(f"Error fetching latest sensor data: {e}")
        return None

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
        logging.info("Successfully inserted data into database")
    except mysql.connector.Error as e:
        logging.error(f"Error uploading data to MySQL: {e}")

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
            timeout=5  # 5 seconds timeout
        )
        response.raise_for_status()
        logging.info(f"Data sent successfully: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending data to Flask API: {e}")
        return False

def process_frame(frame):
    """Process a single frame for detection"""
    results = model.predict(frame, conf=0.25, iou=0.5)
    catfish_count = 0
    dead_catfish_count = 0
    
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = box.conf[0]
            cls = int(box.cls[0])
            
            # Filter out small detections
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

def main():
    logging.info("Starting detection system...")
    print("Press 'q' to exit the detection.")
    
    start_time = datetime.now()
    global dead_catfish_detected, last_capture_time

    try:
        while True:
            # Check for system rest period
            elapsed_time = datetime.now() - start_time
            if elapsed_time >= timedelta(hours=1):
                logging.info("Resting for 5 minutes to prevent overheating...")
                time.sleep(300)
                start_time = datetime.now()

            # Capture frame
            ret, frame = cap.read()
            if not ret:
                logging.error("Error: Failed to capture frame.")
                break

            # Process frame
            frame, catfish_count, dead_catfish_count = process_frame(frame)

            # Send detection data to API
            if catfish_count > 0 or dead_catfish_count > 0:
                if send_detection_data(catfish_count, dead_catfish_count):
                    logging.info(f"Detection data sent - Catfish: {catfish_count}, Dead: {dead_catfish_count}")
                else:
                    logging.warning("Failed to send detection data")

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
                            logging.info("Database updated with new detection data")
                    except Exception as e:
                        logging.error(f"Error handling dead catfish detection: {e}")

            # Display frame
            cv2.imshow("YOLOv8 Real-Time Detection", frame)

            # Check for exit command
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        logging.info("Resources released. Program terminated.")

if __name__ == "__main__":
    main()