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
        const response = await fetch("http://127.0.0.1:5000/temperature");
        const data = await response.json();
        setTemperature(data.temperature);
      } catch (error) {
        console.error("Error fetching temperature data:", error);
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
              {/* {temperature !== null ? `The water temperature is ${getTemperatureStatus()}` : ""} */}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
