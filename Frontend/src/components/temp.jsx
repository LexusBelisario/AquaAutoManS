import React, { useEffect, useState } from "react";
import normTemp from "../images/tempNorm.svg";
import coldTemp from "../images/tempCold.svg";
import hotTemp from "../images/tempHot.svg";
import errorIcon from "../images/errorImg.svg";

export default function Temp() {
  const [temperature, setTemperature] = useState(null);

  useEffect(() => {
    const fetchTemperature = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/temperature"); // Replace with your actual endpoint
        const data = await response.json();
        setTemperature(data.temperature); // Make sure the key matches your API response
      } catch (error) {
        console.error("Error fetching temperature ", error);
      }
    };

    fetchTemperature();

    const interval = setInterval(fetchTemperature, 5000);
    return () => clearInterval(interval);
  }, []);

  const getTemperatureStatus = () => {
    if (temperature >= 26 && temperature <= 32) {
      return "Normal";
    } else if (temperature < 26 && temperature > 20) {
      return "Below Average";
    } else if (temperature <= 20) {
      // Simplified this condition
      return "Too Cold!";
    } else if (temperature > 32 && temperature < 35) {
      return "Above Average";
    } else if (temperature >= 35) {
      return "Too Hot!";
    } else if (temperature < 0 || isNaN(temperature)) {
      // Handle NaN values as errors
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
      // Redundant, already covered above
      return coldTemp;
    } else if (temperature > 32) {
      return hotTemp;
    } else if (temperature < 0 || isNaN(temperature)) {
      // Handle NaN values
      return errorIcon;
    } else {
      return null; // Return null if no image matches to avoid undefined src
    }
  };

  const getLineColor = () => {
    if (temperature >= 26 && temperature <= 32) {
      return "bg-green-500";
    } else if (temperature < 26 && temperature > 20) {
      return "bg-blue-500";
    } else if (temperature <= 20) {
      // Simplified
      return "bg-light-blue-500";
    } else if (temperature > 32 && temperature < 35) {
      return "bg-orange-500";
    } else if (temperature >= 35) {
      return "bg-[#a70000]";
    } else {
      return "bg-gray-200";
    }
  };

  return (
    <div className="bg-slate-50 rounded-md border p-4 border-gray-100 shadow-md h-40 w-72 relative">
      <div
        className={`absolute top-0 left-0 h-full w-2 ${getLineColor()} rounded-tl-md rounded-bl-md`}
      ></div>
      <div className="ml-2 pl-2">
        <div className="flex justify-between">
          <div className="font-bold text-2xl text-black">Temperature</div>
          {getTemperatureImage() && ( // Conditionally render the image
            <img
              className="w-8 h-8"
              src={getTemperatureImage()}
              alt="Temperature Status"
            />
          )}
        </div>
        <div className="flex justify-end mt-4">
          {" "}
          {/* Adjusted margin-top for consistency */}
          <div>
            <p className="text-black font-semibold text-3xl mb-1">
              {" "}
              {/* Added margin-bottom */}
              {temperature !== null ? `${temperature}°C` : "NAN"}{" "}
              {/* Handle null values */}
            </p>
            <div className="flex justify-end mt-2">
              <p className="text-black font-medium text-2xl">
                {getTemperatureStatus()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
