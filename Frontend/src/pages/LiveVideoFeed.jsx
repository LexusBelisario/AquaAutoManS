import React, { useEffect, useRef, useState } from "react";
import io from "socket.io-client";

const LiveVideoFeed = () => {
  const [detectionData, setDetectionData] = useState({
    catfish: 0,
    dead_catfish: 0,
  });
  const [isConnected, setIsConnected] = useState(false);
  const videoRef = useRef(null);
  const socketRef = useRef(null);

  useEffect(() => {
    // Connect to Flask server
    socketRef.current = io("http://localhost:5000");

    socketRef.current.on("connect", () => {
      setIsConnected(true);
      console.log("Connected to server");
    });

    socketRef.current.on("disconnect", () => {
      setIsConnected(false);
      console.log("Disconnected from server");
    });

    socketRef.current.on("detection_data", (data) => {
      setDetectionData(data);
    });

    // Clean up on component unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  useEffect(() => {
    // Access webcam
    const startWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Error accessing webcam:", err);
      }
    };

    startWebcam();

    // Clean up
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, []);

  return (
    <div className="p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gray-800 text-white px-6 py-4">
            <h2 className="text-xl font-semibold">Live Detection Feed</h2>
            <div className="flex items-center mt-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  isConnected ? "bg-green-500" : "bg-red-500"
                } mr-2`}
              ></div>
              <span className="text-sm">
                {isConnected ? "Connected" : "Disconnected"}
              </span>
            </div>
          </div>

          {/* Video Feed */}
          <div className="relative">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-auto"
            />

            {/* Detection Overlay */}
            <div className="absolute top-4 right-4 bg-black bg-opacity-75 text-white p-4 rounded-lg">
              <div className="mb-2">
                <span className="font-semibold">Catfish Detected:</span>
                <span className="ml-2">{detectionData.catfish}</span>
              </div>
              <div>
                <span className="font-semibold">Dead Catfish:</span>
                <span className="ml-2 text-red-500">
                  {detectionData.dead_catfish}
                </span>
              </div>
            </div>
          </div>

          {/* Status Bar */}
          <div className="px-6 py-4 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Last Updated: {new Date().toLocaleTimeString()}
              </div>
              <div className="flex space-x-2">
                <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
                  Capture
                </button>
                <button className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors">
                  Stop
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveVideoFeed;
