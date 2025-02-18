import React, { createContext, useContext, useEffect, useState } from "react";
import io from "socket.io-client";

const WebSocketContext = createContext(null);

export function WebSocketProvider({ children }) {
  const [sensorData, setSensorData] = useState({
    temperature: null,
    oxygen: null,
    phlevel: null,
    turbidity: null,
    catfish: 0,
    dead_catfish: 0,
  });

  useEffect(() => {
    const socket = io("http://localhost:5000");

    socket.on("connect", () => {
      console.log("WebSocket connected");
    });

    socket.on("sensor_update", (data) => {
      setSensorData(data);
    });

    socket.on("disconnect", () => {
      console.log("WebSocket disconnected");
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <WebSocketContext.Provider value={sensorData}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useSensorData() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useSensorData must be used within a WebSocketProvider");
  }
  return context;
}
