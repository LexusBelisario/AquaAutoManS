import cv2
import os
from datetime import datetime

# Function to capture an image and save it to a folder
def capture_image(folder_path):
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Open the webcam
    cap = cv2.VideoCapture(0)  # 0 is the ID for the default camera

    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return

    # Set the resolution to 720p
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    print("Press 's' to capture the image or 'q' to quit.")
    
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Unable to read from the webcam.")
            break

        # Show the frame in a window
        cv2.imshow("Webcam - Press 's' to capture", frame)

        # Wait for a key press
        key = cv2.waitKey(1) & 0xFF

        # 's' to save the image
        if key == ord('s'):
            # Generate a timestamped filename
            filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
            filepath = os.path.join(folder_path, filename)
            
            # Save the image
            cv2.imwrite(filepath, frame)
            print(f"Image saved at {filepath}")
        
        # 'q' to quit
        elif key == ord('q'):
            break

    # Release the webcam and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Specify the folder to save images
folder_path = "hito_new1"
capture_image(folder_path)
