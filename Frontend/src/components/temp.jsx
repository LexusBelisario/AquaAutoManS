import React, { useState, useEffect } from "react";
import { useSensorData } from "../context/WebSocketContext";
import normTemp from "../images/tempNorm.svg";
import coldTemp from "../images/tempCold.svg";
import hotTemp from "../images/tempHot.svg";
import errorIcon from "../images/errorImg.svg";

export default function Temp() {
  const sensorData = useSensorData();
  const temperature = sensorData.temperature;
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (sensorData) {
      setIsLoading(false);
      setError(null);
    } else {
      setError("Connection error");
    }
  }, [sensorData]);

  const getTemperatureStatus = () => {
    if (temperature >= 26 && temperature <= 32) {
      return "Normal";
    } else if (temperature < 26 && temperature > 20) {
      return "Below Average";
    } else if (temperature <= 20 && temperature === 0) {
      return "Too Cold!";
    } else if (temperature > 32 && temperature < 35) {
      return "Above Average";
    } else if (temperature >= 35) {
      return "Too Hot!";
    } else if (temperature < 0) {
      return "Err.";
    } else {
      return "";
    }
  };

  const getTemperatureImage = () => {
    if (temperature >= 26 && temperature <= 32) {
      return normTemp;
    } else if (temperature <= 20) {
      return coldTemp;
    } else if (temperature < 26 && temperature > 20) {
      return coldTemp;
    } else if (temperature > 32) {
      return hotTemp;
    } else if (temperature < 0) {
      return errorIcon;
    }
  };

  const getLineColor = () => {
    if (temperature >= 26 && temperature <= 32) {
      return "bg-green-500";
    } else if (temperature < 26 && temperature > 20) {
      return "bg-blue-500";
    } else if (temperature <= 20 && temperature === 0) {
      return "bg-light-blue-500";
    } else if (temperature > 32 && temperature < 35) {
      return "bg-orange-500";
    } else if (temperature >= 35) {
      return "bg-[#a70000]";
    } else {
      return "bg-gray-200";
    }
  };

  if (isLoading) {
    return (
      <div className="bg-slate-50 rounded-md border p-4 border-gray-100 shadow-md h-40 w-72 relative">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-50 rounded-md border p-4 border-gray-100 shadow-md h-40 w-72 relative">
        <div className="flex items-center justify-center h-full">
          <p className="text-red-500">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-50 rounded-md border p-4 border-gray-100 shadow-md h-40 w-72 relative">
      <div
        className={`absolute top-0 left-0 h-full w-2 ${getLineColor()} rounded-tl-md rounded-bl-md`}
      ></div>
      <div className="ml-2 pl-2">
        <div className="flex justify-between">
          <div className="font-bold text-2xl text-black">Temperature</div>
          <img
            className="w-8 h-8"
            src={getTemperatureImage()}
            alt="Temperature Status"
          />
        </div>
        <div className="flex justify-end mt-2">
          <div>
            <div className="flex justify-end mt-2">
              <p className="text-black font-semibold text-3xl">
                {temperature ? `${temperature}°C` : "NAN"}
              </p>
            </div>
            <p className="text-black font-medium text-2xl mt-2">
              {getTemperatureStatus()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
