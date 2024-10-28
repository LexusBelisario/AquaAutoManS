import cv2
import time
from ultralytics import YOLO

import requests

model = YOLO('C:/Users/user/AquaAutoManS/machine_learning/weights/best.pt')
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open Raspberry Pi camera.")
    exit()

fps = 0
prev_time = time.time()
confidence_threshold = 0.3
resize_factor = 0.5

while True:
    ret, frame = camera.read()
    if not ret:
        print("Error: Could not read frame from Raspberry Pi camera.")
        break

    height, width = frame.shape[:2]
    frame_resized = cv2.resize(frame, (int(width * resize_factor), int(height * resize_factor)))

    curr_time = time.time()
    if int(curr_time - prev_time) >= 1:
        fps = 10 / (curr_time - prev_time)
        prev_time = curr_time

    results = model(frame_resized)

    # Initialize counts for each class
    catfish_count = 0
    dead_catfish_count = 0

    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                conf = box.conf[0]
                if conf > confidence_threshold:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls = int(box.cls[0])
                    label = result.names[cls]

                    # Count detections by class
                    if label == 'catfish':
                        catfish_count += 1
                    elif label == 'dead_catfish':
                        dead_catfish_count += 1

                    # Draw bounding box and label on frame
                    x1, y1 = int(x1 / resize_factor), int(y1 / resize_factor)
                    x2, y2 = int(x2 / resize_factor), int(y2 / resize_factor)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    text = f"{label}: {conf:.2f}"
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Send detection counts to Flask server
    detection_data = {'catfish': catfish_count, 'dead_catfish': dead_catfish_count}
    try:
        response = requests.post("http://localhost:5000/update_detection", json=detection_data)
        print(f"Detection data sent. Response: {response.json()}")
    except Exception as e:
        print(f"Error sending detection data: {e}")

    # Show FPS and display the frame
    fps_text = f"FPS: {fps:.2f}"
    cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("YOLOv8 Object Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()