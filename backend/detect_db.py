import cv2
import requests
import base64
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
from datetime import datetime, timedelta
import mysql.connector
import time

FLASK_API_URL = "http://127.0.0.1:5000/update_detection"

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'dbserial'
}

model = YOLO("C:/Users/user/AquaAutoManS/machine_learning/weights/best1.pt")

class_names = ["catfish", "dead_catfish"]
recent_detections = {"catfish": [], "dead_catfish": []}
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

dead_catfish_detected = False
last_capture_time = None

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

def get_latest_sensor_data():
    """"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True) 

        query = "SELECT * FROM aquamans ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        latest_record = cursor.fetchone()

        cursor.close()
        connection.close()

        return latest_record
    except mysql.connector.Error as e:
        print(f"Error fetching latest sensor data: {e}")
        return None

print("Press 'q' to exit the detection.")

start_time = datetime.now()

while True:
    elapsed_time = datetime.now() - start_time
    if elapsed_time >= timedelta(hours=1):
        print("Resting for 5 minutes to prevent overheating...")
        time.sleep(300)
        start_time = datetime.now() 

    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    results = model.predict(frame, conf=0.25, iou=0.5)
    catfish_count = 0
    dead_catfish_count = 0

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = box.conf[0]
            cls = int(box.cls[0])
            
            if (x2 - x1) < 20 or (y2 - y1) < 20:
                continue
            
            label = f"{class_names[cls]} {conf:.2f}"
            color = (0, 255, 0) if cls == 0 else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            if cls == 0:
                catfish_count += 1
            elif cls == 1:
                dead_catfish_count += 1
                if not dead_catfish_detected:
                    dead_catfish_detected = True

                current_time = datetime.now()
                if last_capture_time is None or (current_time - last_capture_time).total_seconds() >= 20:
                    
                    last_capture_time = current_time

                    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                    img_byte_arr = BytesIO()
                    pil_image.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()

                    latest_data = get_latest_sensor_data()
                    if latest_data is None:
                        print("No latest data available. Skipping image upload.")
                        continue 

                    query = """
                    INSERT INTO aquamans (temperature, tempResult, oxygen, oxygenResult, phlevel, phResult, turbidity, turbidityResult, catfish, dead_catfish, timeData, dead_catfish_image)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
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

                    try:
                        connection = get_db_connection()
                        cursor = connection.cursor()
                        cursor.execute(query, data_to_insert)
                        connection.commit()

                        print(f"Dead catfish detected. Image and latest sensor data uploaded at {current_time}")
                        cursor.close()
                        connection.close()
                    except mysql.connector.Error as e:
                        print(f"Error uploading data to MySQL: {e}")

    data = {
        'catfish': catfish_count,
        'dead_catfish': dead_catfish_count
    }
    try:
        response = requests.post(FLASK_API_URL, json=data)
        if response.status_code == 200:
            print(f"Detection data sent to Flask API: {data}")
        else:
            print(f"Failed to send detection data to Flask API. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to Flask API: {e}")

    recent_detections["catfish"].append(catfish_count)
    recent_detections["dead_catfish"].append(dead_catfish_count)

    if len(recent_detections["catfish"]) > 10:
        recent_detections["catfish"].pop(0)
        recent_detections["dead_catfish"].pop(0)

    catfish_count = int(sum(recent_detections["catfish"]) / len(recent_detections["catfish"]))
    dead_catfish_count = int(sum(recent_detections["dead_catfish"]) / len(recent_detections["dead_catfish"]))

    cv2.imshow("YOLOv8 Real-Time Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
