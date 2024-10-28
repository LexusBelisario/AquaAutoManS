import React, { useEffect, useState } from "react";
import deadfish from "../images/deadFish.svg";

export default function DeadCatfish() {
  const [deadCount, setDeadCount] = useState(0);

  useEffect(() => {
    const fetchDeadCount = async () => {
      try {
        const response = await fetch("http://localhost:5000/data"); // Update with your API endpoint
        const data = await response.json();
        const latestRecord = data[data.length - 1];
        setDeadCount(latestRecord.dead_catfish || 0);
      } catch (error) {
        console.error("Error fetching dead catfish count:", error);
      }
    };

    fetchDeadCount();
    const interval = setInterval(fetchDeadCount, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval); // Cleanup on component unmount
  }, []);

  return (
    <div className="bg-slate-50 rounded-md border p-4 border-gray-100 shadow-md h-40 w-72 relative">
      <div className="absolute top-0 left-0 h-full w-2 bg-red-800 rounded-tl-md rounded-bl-md"></div>
      <div className="ml-2 pl-2">
        <div className="flex justify-between">
          <div className="font-bold text-2xl text-black">Dead Catfish</div>
          <img className="w-8 h-8" src={deadfish} alt="Dead Pic" />
        </div>
        <div className="flex justify-end mt-2">
          <p className="text-black font-semibold text-4xl">{deadCount}</p>
        </div>
      </div>
    </div>
  );
}
