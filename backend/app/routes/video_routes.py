from flask import Blueprint, Response
import cv2
from app.utils.limiters import limiter  # Import your limiter if needed

video_bp = Blueprint('video', __name__)

def generate_frames():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@video_bp.route('/video_feed')
@limiter.exempt  # Exempt from rate limiting if you have it
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')