import cv2
import requests
import base64
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
from datetime import datetime
import mysql.connector
import time  # Import time module

FLASK_API_URL = "http://127.0.0.1:5000/update_detection"

# MySQL Database connection settings
db_config = {
    'host': 'localhost',  # Change to your MySQL host
    'user': 'root',  # Change to your MySQL username
    'password': '',  # Change to your MySQL password
    'database': 'dbserial'  # The database you created earlier
}

# Path to the YOLOv8 model weights
model = YOLO("C:/Users/ADMIN/AquaAutoManS/machine_learning/weights/best3.pt")  # Adjust the path for your system

class_names = ["catfish", "dead_catfish"]
recent_detections = {"catfish": [], "dead_catfish": []}
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Buffer to track detection and detect first dead catfish
dead_catfish_detected = False
last_capture_time = None  # To track when the last capture was made

# Establish a MySQL connection
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

print("Press 'q' to exit the detection.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Perform prediction
    results = model.predict(frame, conf=0.25, iou=0.4)
    catfish_count = 0
    dead_catfish_count = 0

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = box.conf[0]
            cls = int(box.cls[0])

            # Filter small detections
            if (x2 - x1) < 20 or (y2 - y1) < 20:
                continue
            
            label = f"{class_names[cls]} {conf:.2f}"
            color = (0, 255, 0) if cls == 0 else (0, 0, 255)  # Green for catfish, Red for dead catfish
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)  # Draw rectangle
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            if cls == 0:  # catfish
                catfish_count += 1
            elif cls == 1:  # dead_catfish
                dead_catfish_count += 1
                if not dead_catfish_detected:  # Take picture when dead catfish is first detected
                    dead_catfish_detected = True

                # Check if 5 minutes have passed since the last capture
                current_time = datetime.now()
                if last_capture_time is None or (current_time - last_capture_time).total_seconds() >= 20:
                    # Capture new image every 20 seconds
                    last_capture_time = current_time  # Update the last capture time

                    # Convert the frame to image and encode to binary (for uploading)
                    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                    # Convert to binary
                    img_byte_arr = BytesIO()
                    pil_image.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()

                    # Connect to MySQL database and insert image
                    try:
                        connection = get_db_connection()
                        cursor = connection.cursor()

                        # SQL query to insert image into the database
                        query = """
                        INSERT INTO aquamans (dead_catfish_image, timeData)
                        VALUES (%s, %s)
                        """
                        cursor.execute(query, (img_byte_arr, current_time))
                        connection.commit()

                        print(f"Dead catfish detected. Image uploaded to MySQL at {current_time}")

                        # Close the connection
                        cursor.close()
                        connection.close()

                    except mysql.connector.Error as e:
                        print(f"Error uploading to MySQL: {e}")

    # Send the catfish and dead catfish counts to Flask backend
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

    # Show frame
    cv2.imshow("YOLOv8 Real-Time Detection", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
