from ultralytics import YOLO
import cv2
import requests

FLASK_API_URL = "http://127.0.0.1:5000/update_detection"

# Path to the YOLOv8s model weights
model = YOLO("C:/Users/user/AquaAutoManS/machine_learning/weights/best.pt")  # For PC

class_names = ["catfish", "dead_catfish"]

# Buffer to store recent detection counts
recent_detections = {"catfish": [], "dead_catfish": []}

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Start the video stream
print("Press 'q' to exit the detection.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Increase confidence threshold and apply NMS for better filtering
    results = model.predict(frame, conf=1, iou=1)  # Adjust confidence and IoU thresholds

    # Initialize counters
    catfish_count = 0
    dead_catfish_count = 0

    # Parse results
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # Bounding box coordinates
            conf = box.conf[0]  # Confidence score
            cls = int(box.cls[0])  # Class ID

            # Minimum box size to filter small detections
            box_width = x2 - x1
            box_height = y2 - y1
            if box_width < 20 or box_height < 20:  # Filter out very small boxes
                continue

            # Count detections
            if cls == 0:  # catfish
                catfish_count += 1
            elif cls == 1:  # dead_catfish
                dead_catfish_count += 1

            # Draw the bounding box and label
            label = f"{class_names[cls]} {conf:.2f}"
            color = (0, 255, 0) if cls == 0 else (0, 0, 255)  # Green for catfish, Red for dead_catfish
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Add current frame's counts to the buffer
    recent_detections["catfish"].append(catfish_count)
    recent_detections["dead_catfish"].append(dead_catfish_count)

    # Keep the buffer size to the last 10 frames
    if len(recent_detections["catfish"]) > 10:  # Adjust the size (e.g., 10) as needed
        recent_detections["catfish"].pop(0)
        recent_detections["dead_catfish"].pop(0)

    # Calculate the average count over recent frames
    catfish_count = int(sum(recent_detections["catfish"]) / len(recent_detections["catfish"]))
    dead_catfish_count = int(sum(recent_detections["dead_catfish"]) / len(recent_detections["dead_catfish"]))

    # Send detection data to the Flask server
    try:
        response = requests.post(
            FLASK_API_URL,
            json={"catfish": catfish_count, "dead_catfish": dead_catfish_count},
        )
        if response.status_code == 200:
            print("Detection data sent successfully:", response.json())
        else:
            print("Failed to send detection data:", response.text)
    except Exception as e:
        print(f"Error sending detection data: {e}")

    # Display the frame
    cv2.imshow("YOLOv8 Real-Time Detection", frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the resources
cap.release()
cv2.destroyAllWindows()
