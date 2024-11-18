import os
from ultralytics import YOLO
import cv2

VIDEOS_DIR = os.path.join('D:/Folder/Hito')
video_path = os.path.join(VIDEOS_DIR, 'hitoo1.mp4')
video_path_out = '{}_out.mp4'.format(video_path)

cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
if not ret:
    print("Error: Unable to read video file.")
    exit()

H, W, _ = frame.shape

out = cv2.VideoWriter(video_path_out, cv2.VideoWriter_fourcc(*'MP4V'), int(cap.get(cv2.CAP_PROP_FPS)), (W, H))

model_path = r'C:/Users/user/AquaAutoManS/machine_learning/weights/best.pt'
try:
    model = YOLO(model_path)
except Exception as e:
    print(f"Error loading model: {e}")
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    raise

# Confidence and NMS thresholds
confidence_threshold = 0.5  # Minimum confidence for a detection
nms_threshold = 0.4         # Non-Max Suppression IoU threshold

# Class names (adjust according to your model's classes)
class_names = {0: 'catfish', 1: 'dead_catfish'}

while ret:
    # Run YOLO model on the frame
    results = model(frame, conf=confidence_threshold, iou=nms_threshold)[0]

    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result

        # Filter by confidence and specific classes
        if score > confidence_threshold and int(class_id) in class_names:
            # Draw bounding box
            color = (0, 255, 0) if int(class_id) == 0 else (0, 0, 255)  # Green for catfish, red for dead catfish
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

            # Add label
            label = f"{class_names[int(class_id)].upper()} {score:.2f}"
            cv2.putText(frame, label, (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)

    # Write the frame to output video
    out.write(frame)

    # Read next frame
    ret, frame = cap.read()

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()
