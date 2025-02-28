# video_routes.py
from flask import Blueprint, Response, jsonify
import cv2
from app.utils.limiters import limiter
from flask_cors import CORS
import logging
import time

video_bp = Blueprint('video', __name__)
CORS(video_bp)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def init_camera():
    try:
        # Try DirectShow first (for Windows)
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not camera.isOpened():
            # If DirectShow fails, try default
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                logger.error("Failed to open camera with both methods")
                return None

        # Set camera properties
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        # Wait for camera to initialize
        time.sleep(2)
        
        # Test frame capture
        ret, frame = camera.read()
        if not ret or frame is None:
            logger.error("Failed to capture test frame")
            camera.release()
            return None
            
        logger.info(f"Camera initialized: Resolution={frame.shape}, Type={frame.dtype}")
        return camera
        
    except Exception as e:
        logger.error(f"Camera initialization error: {str(e)}")
        return None

def generate_frames():
    camera = init_camera()
    if camera is None:
        logger.error("Camera initialization failed")
        return

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                logger.error("Failed to read frame")
                break

            # Add debug information to frame
            cv2.putText(frame, f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Frame Size: {frame.shape}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                logger.error("Failed to encode frame")
                break

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    except Exception as e:
        logger.error(f"Frame generation error: {str(e)}")
    finally:
        camera.release()

@video_bp.route('/video_feed')
@limiter.exempt
def video_feed():
    try:
        return Response(
            generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame',
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'Access-Control-Allow-Origin': '*'
            }
        )
    except Exception as e:
        logger.error(f"Video feed error: {str(e)}")
        return jsonify({
            'error': 'Video feed error',
            'message': str(e)
        }), 500

@video_bp.route('/test_camera')
def test_camera():
    """Test endpoint to verify camera functionality"""
    try:
        camera = init_camera()
        if camera is None:
            return jsonify({
                'status': 'error',
                'message': 'Failed to initialize camera'
            }), 500

        ret, frame = camera.read()
        camera.release()

        if not ret:
            return jsonify({
                'status': 'error',
                'message': 'Failed to capture test frame'
            }), 500

        return jsonify({
            'status': 'success',
            'message': 'Camera test successful',
            'frame_shape': str(frame.shape),
            'frame_type': str(frame.dtype)
        })

    except Exception as e:
        logger.error(f"Camera test error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500