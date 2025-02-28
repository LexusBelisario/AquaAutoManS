import React, { useState, useEffect } from "react";

const LiveVideoFeed = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isResting, setIsResting] = useState(false);
  const [nextRest, setNextRest] = useState(null);
  const [detectionData, setDetectionData] = useState({
    catfish: 0,
    deadCatfish: 0,
  });

  // Fetch system status
  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        const response = await fetch(
          "http://localhost:5000/video/system_status"
        );
        const data = await response.json();

        if (data.status === "success") {
          setIsResting(data.is_resting);
          setNextRest(data.next_rest);
        }
      } catch (error) {
        console.error("Error checking system status:", error);
      }
    };

    const interval = setInterval(checkSystemStatus, 1000);
    return () => clearInterval(interval);
  }, []);

  // Format time remaining
  const formatTimeRemaining = (seconds) => {
    if (!seconds) return "";
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  return (
    <div className="flex flex-col items-center p-4 bg-gray-100 rounded-lg shadow-lg">
      {/* Rest Status Banner */}
      {isResting && (
        <div className="w-full bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-yellow-500"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                System is resting for 5 minutes to prevent overheating
                {nextRest && (
                  <span className="font-medium">
                    {" "}
                    (Resuming in {formatTimeRemaining(nextRest)})
                  </span>
                )}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Next Rest Timer (when not resting) */}
      {!isResting && nextRest && (
        <div className="w-full bg-blue-100 border-l-4 border-blue-500 p-4 mb-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-blue-500"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                Next system rest in {formatTimeRemaining(nextRest)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Video Display */}
      <div className="w-full max-w-4xl bg-white rounded-lg overflow-hidden">
        <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
              <p className="text-red-500 text-center p-4">{error}</p>
            </div>
          )}

          <img
            src="http://localhost:5000/video/video_feed"
            alt="Live video feed"
            className="w-full h-full object-contain"
            onLoad={() => setIsLoading(false)}
            onError={(e) => {
              console.error("Video feed error:", e);
              setError("Failed to load video feed");
              setIsLoading(false);
            }}
          />

          {/* Detection Counts Overlay */}
          <div className="absolute top-4 right-4 bg-black bg-opacity-50 rounded-lg p-3">
            <p className="text-white font-semibold">
              Live Catfish: {detectionData.catfish}
            </p>
            <p className="text-white font-semibold">
              Dead Catfish: {detectionData.deadCatfish}
            </p>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center">
            <div
              className={`w-3 h-3 rounded-full ${
                isResting
                  ? "bg-yellow-500"
                  : isLoading
                  ? "bg-blue-500"
                  : error
                  ? "bg-red-500"
                  : "bg-green-500"
              } mr-2`}
            ></div>
            <span className="text-gray-600">
              {isResting
                ? "System Resting"
                : isLoading
                ? "Connecting..."
                : error
                ? "Error"
                : "System Active"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveVideoFeed;
