# app/routes/video_routes.py
from flask import Blueprint, Response, jsonify
import cv2
from app.utils.limiters import limiter
from flask_cors import CORS
import logging
import time
from ultralytics import YOLO
from datetime import datetime, timedelta
from app import db
from app.models import aquamans
from PIL import Image
from io import BytesIO

video_bp = Blueprint('video', __name__)
CORS(video_bp)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_detect.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load YOLO model
try:
    model = YOLO("C:/Users/ADMIN/AquaAutoManS/machine_learning/weights/best1.pt")
    class_names = ["catfish", "dead_catfish"]
    logger.info("YOLO model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {str(e)}")
    model = None

# Initialize detection variables
dead_catfish_detected = False
last_capture_time = None

def init_camera():
    """Initialize and configure camera"""
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            logger.error("Failed to open camera")
            return None

        # Set camera properties
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        # Test camera
        ret, _ = camera.read()
        if not ret:
            logger.error("Failed to read test frame")
            return None
            
        logger.info("Camera initialized successfully")
        return camera
    except Exception as e:
        logger.error(f"Camera initialization error: {str(e)}")
        return None

def process_frame(frame):
    """Process frame with YOLO detection"""
    try:
        if model is None:
            return frame, 0, 0

        # Run detection
        results = model.predict(frame, conf=0.25, iou=0.5)
        catfish_count = 0
        dead_catfish_count = 0

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # Filter out small detections
                if (x2 - x1) < 20 or (y2 - y1) < 20:
                    continue
                
                label = f"{class_names[cls]} {conf:.2f}"
                color = (0, 255, 0) if cls == 0 else (0, 0, 255)
                
                # Draw detection box and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                if cls == 0:
                    catfish_count += 1
                else:
                    dead_catfish_count += 1

        return frame, catfish_count, dead_catfish_count

    except Exception as e:
        logger.error(f"Error in process_frame: {str(e)}")
        return frame, 0, 0

def update_database(frame, catfish_count, dead_catfish_count):
    """Update database with detection results"""
    try:
        # Get latest sensor data
        latest_data = db.session.query(aquamans).order_by(aquamans.id.desc()).first()
        
        if latest_data:
            current_time = datetime.now()
            
            # Convert frame to JPEG if dead catfish detected
            img_bytes = None
            if dead_catfish_count > 0:
                pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img_byte_arr = BytesIO()
                pil_image.save(img_byte_arr, format='JPEG')
                img_bytes = img_byte_arr.getvalue()

            # Create new record
            new_record = aquamans(
                temperature=latest_data.temperature,
                tempResult=latest_data.tempResult,
                oxygen=latest_data.oxygen,
                oxygenResult=latest_data.oxygenResult,
                phlevel=latest_data.phlevel,
                phResult=latest_data.phResult,
                turbidity=latest_data.turbidity,
                turbidityResult=latest_data.turbidityResult,
                catfish=catfish_count,
                dead_catfish=dead_catfish_count,
                timeData=current_time,
                dead_catfish_image=img_bytes
            )

            db.session.add(new_record)
            db.session.commit()
            logger.info(f"Database updated - Catfish: {catfish_count}, Dead: {dead_catfish_count}")

    except Exception as e:
        logger.error(f"Database update error: {str(e)}")
        db.session.rollback()

def generate_frames():
    """Generate video frames with detection"""
    camera = init_camera()
    if camera is None:
        return

    start_time = datetime.now()
    last_db_update = time.time()
    db_update_interval = 20  # Update database every 20 seconds

    try:
        while True:
            # Check for hourly rest period
            elapsed_time = datetime.now() - start_time
            if elapsed_time >= timedelta(hours=1):
                logger.info("Resting for 5 minutes to prevent overheating...")
                camera.release()
                time.sleep(300)  # Rest for 5 minutes
                
                # Reinitialize camera after rest
                camera = init_camera()
                if camera is None:
                    return
                    
                start_time = datetime.now()
                logger.info("Resuming after rest period")
                continue

            # Capture frame
            ret, frame = camera.read()
            if not ret:
                logger.error("Failed to capture frame")
                time.sleep(1)
                continue

            # Process frame with detection
            frame, catfish_count, dead_catfish_count = process_frame(frame)

            # Add timestamp and counts to frame
            cv2.putText(frame, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Live Catfish: {catfish_count}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Dead Catfish: {dead_catfish_count}", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Update database periodically
            current_time = time.time()
            if current_time - last_db_update >= db_update_interval:
                update_database(frame, catfish_count, dead_catfish_count)
                last_db_update = current_time

            # Encode and yield frame
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    except Exception as e:
        logger.error(f"Error in generate_frames: {str(e)}")
    finally:
        if camera is not None:
            camera.release()

@video_bp.route('/video_feed')
@limiter.exempt
def video_feed():
    """Video streaming route"""
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
        return jsonify({'error': str(e)}), 500

@video_bp.route('/detection_status')
def detection_status():
    """Get current detection status"""
    try:
        latest_record = db.session.query(aquamans).order_by(aquamans.id.desc()).first()
        return jsonify({
            'status': 'success',
            'catfish_count': latest_record.catfish if latest_record else 0,
            'dead_catfish_count': latest_record.dead_catfish if latest_record else 0,
            'last_update': latest_record.timeData.isoformat() if latest_record else None
        })
    except Exception as e:
        logger.error(f"Error getting detection status: {str(e)}")
        return jsonify({'error': str(e)}), 500