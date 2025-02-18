import io from "socket.io-client";

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
  }

  connect() {
    if (!this.socket) {
      this.socket = io("http://localhost:5000");
      this.socket.on("connect", () => {
        console.log("WebSocket connected");
      });

      this.socket.on("sensor_update", (data) => {
        this.listeners.forEach((callback) => callback(data));
      });
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  subscribe(id, callback) {
    this.listeners.set(id, callback);
  }

  unsubscribe(id) {
    this.listeners.delete(id);
  }
}

export default new WebSocketService();
