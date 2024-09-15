import React from "react";

export default function LiveMonitoring() {
  return (
    <div>
      <h1>Live Monitoring</h1>
      <img
        src="http://localhost:5000/video_feed"
        alt="Live Feed"
        style={{ width: "100%", height: "auto" }}
      />
    </div>
  );
}
