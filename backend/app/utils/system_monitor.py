import psutil
import threading
import time
from datetime import datetime

class SystemHealthCheck:
    def __init__(self):
        self.health_data = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'last_updated': None
        }
        self.start_monitoring()

    def start_monitoring(self):
        def monitor():
            while True:
                self.health_data.update({
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent,
                    'last_updated': datetime.utcnow().isoformat()
                })
                time.sleep(60)  # Update every minute

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def get_health_status(self):
        status = 'healthy'
        issues = []

        if self.health_data['cpu_usage'] > 80:
            status = 'warning'
            issues.append('High CPU usage')

        if self.health_data['memory_usage'] > 80:
            status = 'warning'
            issues.append('High memory usage')

        if self.health_data['disk_usage'] > 80:
            status = 'warning'
            issues.append('High disk usage')

        return {
            'status': status,
            'metrics': self.health_data,
            'issues': issues,
            'timestamp': datetime.utcnow().isoformat()
        }