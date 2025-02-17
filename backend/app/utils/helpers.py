import logging
import threading
import time

class SystemMonitor:
    def __init__(self):
        self.active = True
        self.setup_logging()
        self.start_monitoring()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def periodic_sleep(self):
        """Manages system's periodic rest periods to prevent overheating."""
        while True:
            logging.info("System active.")
            time.sleep(3600 - 300)  # Run for 55 minutes
            logging.info("System will sleep for 5 minutes to prevent overheating.")
            self.active = False
            time.sleep(300)  # Sleep for 5 minutes
            self.active = True
            logging.info("System resumed.")

    def background_task(self):
        """Executes background tasks when system is active."""
        while True:
            if not self.active:
                logging.info("Task paused due to system rest period.")
                time.sleep(300)
                continue
            
            logging.info("Task executed.")
            time.sleep(60)

    def start_monitoring(self):
        """Starts the monitoring threads."""
        sleep_thread = threading.Thread(target=self.periodic_sleep, daemon=True)
        sleep_thread.start()

        task_thread = threading.Thread(target=self.background_task, daemon=True)
        task_thread.start()

    def is_active(self):
        """Returns the current system status."""
        return self.active