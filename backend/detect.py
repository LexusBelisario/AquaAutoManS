from ultralytics import YOLO
import cv2

model = YOLO("C:/Users/user/AquaAutoManS/machine_learning/weights/best.pt") 


class_names = ["catfish", "dead_catfish"]


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

    # Predict with YOLOv8 model
    results = model.predict(frame, conf=0.7)  # Adjust confidence threshold as needed

    # Parse results
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # Bounding box coordinates
            conf = box.conf[0]  # Confidence score
            cls = int(box.cls[0])  # Class ID

            # Draw the bounding box and label
            label = f"{class_names[cls]} {conf:.2f}"
            color = (0, 255, 0) if cls == 0 else (0, 0, 255)  # Green for catfish, Red for dead_catfish
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Display the frame
    cv2.imshow("YOLOv8 Real-Time Detection", frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the resources
cap.release()
cv2.destroyAllWindows()
