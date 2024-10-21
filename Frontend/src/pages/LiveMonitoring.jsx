import React, { useEffect, useState } from "react";

export default function LiveMonitoring() {
  const [error, setError] = useState("");

  useEffect(() => {
    const checkCameraFeed = async () => {
      try {
        const response = await fetch("http://localhost:5000/camera_feed");
        if (!response.ok) {
          const data = await response.json();
          setError(data.error);
        }
      } catch (err) {
        setError("No Camera Detected.");
      }
    };

    checkCameraFeed();
  }, []);

  return (
    <div>
      {error ? (
        <div style={{ color: "red" }}>{error}</div>
      ) : (
        <img
          src="http://localhost:5000/camera_feed"
          alt="Live Feed"
          style={{ width: "100%", height: "auto" }}
        />
      )}
    </div>
  );
}
