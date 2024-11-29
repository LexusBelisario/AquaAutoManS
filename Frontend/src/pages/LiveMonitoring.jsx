import React, { useEffect, useState } from "react";

export default function LiveMonitoring() {
  const [detectionData, setDetectionData] = useState(null);

  // Fetch detection data from the backend
  useEffect(() => {
    const fetchDetectionData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/detection_data");
        if (response.ok) {
          const data = await response.json();
          setDetectionData(data);
        } else {
          console.error("Failed to fetch detection data:", response.status);
        }
      } catch (error) {
        console.error("Error fetching detection data:", error);
      }
    };

    // Poll the backend every 5 seconds
    const intervalId = setInterval(fetchDetectionData, 5000);

    // Cleanup on component unmount
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div style={{ textAlign: "center", margin: "20px" }}>
      <h1>Live Monitoring</h1>
      {/* Display video feed */}
      <div style={{ marginBottom: "20px" }}>
        <h2>Real-Time Video Feed</h2>
        <img
          src="http://127.0.0.1:5000/video_feed"
          alt="Live Monitoring"
          style={{ width: "80%", border: "1px solid #ccc" }}
        />
      </div>

      {/* Display detection data */}
      <div>
        <h2>Detection Data</h2>
        {detectionData ? (
          <div>
            <p>
              <strong>Catfish Count:</strong> {detectionData.catfish}
            </p>
            <p>
              <strong>Dead Catfish Count:</strong> {detectionData.dead_catfish}
            </p>
            <p>
              <strong>Last Update:</strong>{" "}
              {new Date(detectionData.timeData).toLocaleString()}
            </p>
          </div>
        ) : (
          <p>Loading detection data...</p>
        )}
      </div>
    </div>
  );
}
