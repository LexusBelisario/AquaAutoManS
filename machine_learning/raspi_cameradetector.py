import cv2
import time
from ultralytics import YOLO

# Load your trained YOLOv8 model
model = YOLO('C:/Users/user/AquaAutoManS/machine_learning/weights/best.pt')

# Set up the USB Webcam (use '0' or '1' depending on which camera is assigned to the USB webcam)
camera = cv2.VideoCapture(0)  # Change index to '1' if you have multiple cameras and this doesn't work

# Check if the camera opened successfully
if not camera.isOpened():
    print("Error: Could not open USB webcam.")
    exit()

fps = 0
prev_time = time.time()

confidence_threshold = 0.7
resize_factor = 0.5

while True:
    ret, frame = camera.read()
    if not ret:
        print("Error: Could not read frame from USB webcam.")
        break

    height, width = frame.shape[:2]
    frame_resized = cv2.resize(frame, (int(width * resize_factor), int(height * resize_factor)))

    curr_time = time.time()
    if int(curr_time - prev_time) >= 1:
        fps = 10 / (curr_time - prev_time)
        prev_time = curr_time

    # Run YOLOv8 model inference
    results = model(frame_resized, conf=confidence_threshold, iou=0.4, agnostic_nms=True)  # Adjust the iou as needed


    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                conf = box.conf[0]
                if conf > confidence_threshold:  
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls = int(box.cls[0])
                    label = result.names[cls]

                    print(f"Detected {label} with confidence {conf:.2f} at [{x1}, {y1}, {x2}, {y2}]")

                    # Rescale the bounding box coordinates to the original frame size
                    x1, y1 = int(x1 / resize_factor), int(y1 / resize_factor)
                    x2, y2 = int(x2 / resize_factor), int(y2 / resize_factor)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    text = f"{label}: {conf:.2f}"
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display FPS on the frame
    fps_text = f"FPS: {fps:.2f}"
    cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow("YOLOv8 Object Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
camera.release()
cv2.destroyAllWindows()
