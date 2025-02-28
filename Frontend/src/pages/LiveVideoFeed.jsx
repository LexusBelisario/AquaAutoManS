// LiveVideoFeed.jsx
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const LiveVideoFeed = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [detectionData, setDetectionData] = useState({
    catfish: 0,
    deadCatfish: 0
  });
  const imageRef = useRef(null);

  // Function to handle image loading
  const handleImageLoad = () => {
    setIsLoading(false);
    setError(null);
  };

  // Function to handle image error
  const handleImageError = () => {
    setIsLoading(false);
    setError('Failed to load video feed');
    // Attempt to reload the image after a short delay
    setTimeout(() => {
      if (imageRef.current) {
        imageRef.current.src = `http://localhost:5000/video/video_feed?t=${new Date().getTime()}`;
      }
    }, 5000);
  };

  // Fetch detection data
  useEffect(() => {
    const fetchDetectionData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/latest-detection');
        setDetectionData({
          catfish: response.data.catfish || 0,
          deadCatfish: response.data.dead_catfish || 0
        });
      } catch (error) {
        console.error('Error fetching detection data:', error);
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
        
        {/* Video Display Container */}
        <div className="relative aspect-video bg-black rounded-lg overflow-hidden mb-4">
          {/* Loading Spinner */}
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          )}
          
          {/* Error Message */}
          {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
              <div className="text-white text-center p-4">
                <p className="text-red-500 mb-2">{error}</p>
                <button 
                  onClick={() => {
                    setIsLoading(true);
                    setError(null);
                    if (imageRef.current) {
                      imageRef.current.src = `http://localhost:5000/video/video_feed?t=${new Date().getTime()}`;
                    }
                  }}
                  className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                >
                  Retry Connection
                </button>
              </div>
            </div>
          )}

          {/* Video Feed */}
          <img
            ref={imageRef}
            src={`http://localhost:5000/video/video_feed`}
            alt="Live video feed"
            className="w-full h-full object-contain"
            onLoad={handleImageLoad}
            onError={handleImageError}
          />
          
          {/* Detection Overlay */}
          <div className="absolute top-4 left-4 bg-black bg-opacity-50 rounded-lg p-3">
            <p className="text-white font-semibold">
              Catfish: {detectionData.catfish}
            </p>
            <p className="text-white font-semibold">
              Dead Catfish: {detectionData.deadCatfish}
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
              <div className={`w-3 h-3 rounded-full ${isLoading ? 'bg-yellow-500' : error ? 'bg-red-500' : 'bg-green-500'} mr-2`}></div>
              <span className="text-gray-600">
                {isLoading ? 'Connecting...' : error ? 'Error' : 'Connected'}
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
      </div>
    </div>
  );
};

export default LiveVideoFeed;