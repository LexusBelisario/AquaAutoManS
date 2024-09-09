import React, { useEffect, useState } from "react";
import clean from "../images/cleanWater.svg";
import dirty from "../images/dirtyWater.svg";
import cloudy from "../images/cloudyWater.svg";

export default function turbidityy() {
  const [turbidity, setTurbidity] = useState(null);

  useEffect(() => {
    const fetchTurbidity = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/turbidity"); // Update the URL to your Flask API endpoint
        const data = await response.json();
        setTurbidity(data.turbidity);
      } catch (error) {
        console.error("Error fetching turbidity data:", error);
      }
    };

    fetchTurbidity();

    const interval = setInterval(fetchTurbidity, 5000); // Fetch new data every 5 seconds
    return () => clearInterval(interval); // Cleanup the interval on component unmount
  }, []);

  const getTurbidityStatus = () => {
    if (turbidity < 20) {
      return "Clean";
    } else if (turbidity <= 49) {
      return "Cloudy";
    } else if (turbidity >= 50) {
      return "Dirty";
    } else if (turbidity <= 60) {
      return "Super Dirty";
    }
  };

  const getTurbidityImage = () => {
    if (turbidity < 20) {
      return clean;
    } else if (turbidity <= 49) {
      return cloudy;
    } else if (turbidity >= 50) {
      return dirty;
    } else if (turbidity <= 60) {
      return dirty;
    }
  };

  const getLineColor = () => {
    if (turbidity < 20) {
      return "bg-[#066cfa]";
    } else if (turbidity <= 49) {
      return "bg-[#a8b7c8]";
    } else if (turbidity >= 50) {
      return "bg-[#733a00]";
    } else if (turbidity <= 60) {
      return "bg-[#502f0c]";
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
          <div className="font-bold text-2xl text-black">Water Turbidity</div>
          <img
            className="w-8 h-8"
            src={getTurbidityImage()}
            alt="Turbidity Status"
          />
        </div>
        <div className="flex justify-end mb-2 mt-4">
          <div>
            <div className="flex justify-end">
              <p className="text-black font-semibold text-3xl mb-1">
                {turbidity ? `${turbidity} V` : "NAN"}
              </p>
            </div>
            <p className="text-black font-medium text-2xl">
              {turbidity !== null ? `The water is ${getTurbidityStatus()}` : ""}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
