import React, { useEffect, useState } from "react";
import oxygenLow from "../images/oxygenLow.svg";
import oxygenBelowAve from "../images/oxygenBelowAve.svg";
import oxygenAve from "../images/oxygenNormal.svg";
import oxygenHigh from "../images/oxygenHigh.svg";

export default function oxygenn() {
  const [oxygen, setOxygen] = useState(null);

  useEffect(() => {
    const fetchOxygen = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/oxygen");
        const data = await response.json();
        setOxygen(data.oxygen);
      } catch (error) {
        console.error("Error fetching oxygen data:", error);
      }
    };

    fetchOxygen();

    const interval = setInterval(fetchOxygen, 5000);
    return () => clearInterval(interval);
  }, []);

  const getOxygenConditionMessage = () => {
    if (oxygen === 0) {
      return "Too Low";
    } else if (oxygen < 1.5) {
      return "Low";
    } else if (oxygen >= 1.5 && oxygen <= 5) {
      return "Normal";
    } else if (oxygen > 5) {
      return "High Oxygen Level";
    } else {
      return "";
    }
  };

  const getOxygenImage = () => {
    if (oxygen === 0) {
      return oxygenLow;
    } else if (oxygen < 1.5) {
      return oxygenBelowAve;
    } else if (oxygen >= 1.5 && oxygen <= 5) {
      return oxygenAve;
    } else if (oxygen > 5) {
      return oxygenHigh;
    }
  };

  const getLineColor = () => {
    if (oxygen === 0) {
      return "bg-[#a70000]";
    } else if (oxygen < 1.5) {
      return "bg-orange-200";
    } else if (oxygen >= 1.5 && oxygen <= 5) {
      return "bg-[#399918]";
    } else if (oxygen > 5) {
      return "bg-[#4F1787]";
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
          <div className="font-bold text-2xl text-black">Oxygen</div>
          <img className="w-8 h-8" src={getOxygenImage()} alt="Oxygen Status" />
        </div>
        <div className="flex justify-end mt-4">
          <div>
            <p className="text-black font-semibold text-3xl mb-1">
              {oxygen ? `${oxygen} mg/l` : "NAN"}
            </p>
            <div className="flex justify-end mt-2">
              <p className="text-black font-medium text-2xl">
                {oxygen ? getOxygenConditionMessage() : ""}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
