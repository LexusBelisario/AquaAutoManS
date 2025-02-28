import threading
import cv2
import time
from datetime import datetime, timedelta
import logging
from app import db
from app.models import aquamans
from ultralytics import YOLO

class DetectionService:
    def __init__(self):
        self.is_running = False
        self.camera = None
        self.detection_thread = None
        self.model = YOLO("C:/Users/ADMIN/AquaAutoManS/machine_learning/weights/best1.pt")
        self.class_names = ["catfish", "dead_catfish"]
        self.start_time = None
        
    def start_detection(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = datetime.now()
            self.detection_thread = threading.Thread(target=self._detection_loop)
            self.detection_thread.daemon = True
            self.detection_thread.start()
            logging.info("Detection service started")
            
    def stop_detection(self):
        self.is_running = False
        if self.camera:
            self.camera.release()
        logging.info("Detection service stopped")
        
    def _detection_loop(self):
        self.camera = cv2.VideoCapture(0)
        last_db_update = time.time()
        
        while self.is_running:
            try:
                # Check for hourly rest
                elapsed_time = datetime.now() - self.start_time
                if elapsed_time >= timedelta(hours=1):
                    logging.info("Taking 5-minute rest...")
                    time.sleep(300)  # 5 minutes rest
                    self.start_time = datetime.now()
                    continue

                ret, frame = self.camera.read()
                if not ret:
                    continue

                # Process frame
                results = self.model.predict(frame, conf=0.25, iou=0.5)
                catfish_count = 0
                dead_catfish_count = 0

                for result in results:
                    for box in result.boxes:
                        cls = int(box.cls[0])
                        if cls == 0:
                            catfish_count += 1
                        else:
                            dead_catfish_count += 1

                # Update database every 20 seconds
                current_time = time.time()
                if current_time - last_db_update >= 20:
                    self._update_database(frame, catfish_count, dead_catfish_count)
                    last_db_update = current_time

            except Exception as e:
                logging.error(f"Error in detection loop: {str(e)}")
                time.sleep(1)

        if self.camera:
            self.camera.release()

    def _update_database(self, frame, catfish_count, dead_catfish_count):
        try:
            latest_data = db.session.query(aquamans).order_by(aquamans.id.desc()).first()
            if latest_data:
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
                    timeData=datetime.now()
                )
                db.session.add(new_record)
                db.session.commit()
                logging.info(f"Database updated - Live: {catfish_count}, Dead: {dead_catfish_count}")
        except Exception as e:
            logging.error(f"Database update error: {str(e)}")
            db.session.rollback()

# Create global instance
detection_service = DetectionService()