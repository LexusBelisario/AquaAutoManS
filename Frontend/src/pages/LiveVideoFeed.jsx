// LiveVideoFeed.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";

const LiveVideoFeed = () => {
  const [detectionData, setDetectionData] = useState({
    catfish: 0,
    deadCatfish: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch detection data
  useEffect(() => {
    const fetchDetectionData = async () => {
      try {
        const response = await axios.get(
          "http://localhost:5000/api/latest-detection"
        );
        setDetectionData({
          catfish: response.data.catfish,
          deadCatfish: response.data.dead_catfish,
        });
      } catch (error) {
        console.error("Error fetching detection data:", error);
      }
    };

    const interval = setInterval(fetchDetectionData, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center p-4 bg-gray-100 min-h-screen">
      <div className="w-full max-w-4xl bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Live Detection Feed
        </h2>

        {/* Video Display */}
        <div className="relative aspect-video bg-black rounded-lg overflow-hidden mb-4">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50">
              <p className="text-red-500 text-center p-4">{error}</p>
            </div>
          )}

          <img
            src="http://localhost:5000/video/video_feed"
            alt="Live video feed"
            className="w-full h-full object-contain"
            onLoad={() => setIsLoading(false)}
            onError={(e) => {
              setError("Failed to load video feed");
              setIsLoading(false);
              console.error("Video feed error:", e);
            }}
            style={{ maxHeight: "480px" }}
          />

          {/* Detection Overlay */}
          <div className="absolute top-4 left-4 bg-black bg-opacity-50 rounded-lg p-3">
            <p className="text-white font-semibold">
              Catfish Detected: {detectionData.catfish}
            </p>
            <p className="text-white font-semibold">
              Dead Catfish Detected: {detectionData.deadCatfish}
            </p>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-700">
              Camera Status
            </h3>
            <div className="flex items-center mt-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  isLoading
                    ? "bg-yellow-500"
                    : error
                    ? "bg-red-500"
                    : "bg-green-500"
                } mr-2`}
              ></div>
              <span className="text-gray-600">
                {isLoading ? "Connecting..." : error ? "Error" : "Connected"}
              </span>
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-700">
              Detection Status
            </h3>
            <div className="flex items-center mt-2">
              <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
              <span className="text-gray-600">Active</span>
            </div>
          </div>
        </div>

        {/* Detection Statistics */}
        <div className="mt-6 grid grid-cols-2 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-700">
              Live Catfish
            </h3>
            <p className="text-3xl font-bold text-blue-800 mt-2">
              {detectionData.catfish}
            </p>
          </div>

          <div className="bg-red-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-red-700">Dead Catfish</h3>
            <p className="text-3xl font-bold text-red-800 mt-2">
              {detectionData.deadCatfish}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveVideoFeed;
