import React, { useState, useEffect } from "react";
import io from "socket.io-client";

const LiveFeed = () => {
  const [detectionData, setDetectionData] = useState({
    catfish: 0,
    dead_catfish: 0,
  });
  const [latestImage, setLatestImage] = useState(null);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const newSocket = io("http://localhost:5000");
    setSocket(newSocket);

    newSocket.on("detection_data", (data) => {
      setDetectionData(data);
    });

    const fetchLatestImage = async () => {
      try {
        const response = await fetch("http://localhost:5000/latest-image");
        if (response.ok) {
          const blob = await response.blob();
          setLatestImage(URL.createObjectURL(blob));
        }
      } catch (error) {
        console.error("Error fetching latest image:", error);
      }
    };

    fetchLatestImage();
    const imageInterval = setInterval(fetchLatestImage, 5000);

    return () => {
      if (newSocket) newSocket.close();
      clearInterval(imageInterval);
    };
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Live Detection Feed
      </h2>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* Live Catfish Stats */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            Live Catfish
          </h3>
          <p className="text-3xl font-bold text-blue-600">
            {detectionData.catfish}
          </p>
        </div>

        {/* Dead Catfish Stats */}
        <div className="bg-red-50 rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            Dead Catfish
          </h3>
          <p className="text-3xl font-bold text-red-600">
            {detectionData.dead_catfish}
          </p>
        </div>
      </div>

      {/* Camera Feed */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">
          Camera Feed
        </h3>

        {latestImage ? (
          <div className="relative aspect-video">
            <img
              src={latestImage}
              alt="Latest detection"
              className="rounded-lg w-full h-full object-cover"
            />
          </div>
        ) : (
          <div className="bg-gray-100 rounded-lg p-10 text-center">
            <p className="text-gray-500">No camera feed available</p>
          </div>
        )}
      </div>

      {/* Additional Information */}
      <div className="mt-6 bg-blue-50 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          Live feed updates automatically every 5 seconds
        </p>
      </div>
    </div>
  );
};

export default LiveFeed;
