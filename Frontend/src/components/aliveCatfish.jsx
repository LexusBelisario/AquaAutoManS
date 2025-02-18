import React, { useState, useEffect } from "react";
import fish from "../images/fishCat.svg";
import { useSensorData } from "../context/WebSocketContext";

export default function AliveCatfish() {
  const sensorData = useSensorData();
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (sensorData) {
      setIsLoading(false);
      setError(null);
    } else {
      setError("Connection error");
    }
  }, [sensorData]);

  return (
    <div className="bg-slate-50 rounded-md border p-4 border-gray-100 shadow-md h-40 w-72 relative">
      <div className="absolute top-0 left-0 h-full w-2 bg-[#5f4d4d] rounded-tl-md rounded-bl-md"></div>
      <div className="ml-2 pl-2">
        <div className="flex justify-between">
          <div className="font-bold text-2xl text-black">Alive Catfish</div>
          <img className="w-8 h-8" src={fish} alt="Alive Pic" />
        </div>
        <div className="flex justify-end mt-2">
          {isLoading ? (
            <div className="animate-pulse bg-gray-200 h-8 w-16 rounded"></div>
          ) : error ? (
            <p className="text-red-500 text-sm">{error}</p>
          ) : (
            <p className="text-black font-semibold text-4xl">
              {sensorData.catfish || 0}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
