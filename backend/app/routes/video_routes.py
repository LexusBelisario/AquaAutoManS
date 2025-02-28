# video_routes.py
from flask import Blueprint, Response
import cv2
from app.utils.limiters import limiter

video_bp = Blueprint('video', __name__)

def generate_frames():
    cap = cv2.VideoCapture(0)  # Use 0 for default webcam
    
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()

@video_bp.route('/video_feed')
@limiter.exempt
def video_feed():
    try:
        return Response(generate_frames(),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        return str(e), 500