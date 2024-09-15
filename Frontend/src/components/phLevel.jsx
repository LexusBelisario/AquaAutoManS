import React, { useEffect, useState } from "react";
import phAcid from "../images/phAcidic.svg";
import phBelowAve from "../images/phBelowAve.svg";
import phAverage from "../images/phNormal.svg";
import phAboveAve from "../images/phAboveAve.svg";
import phAlka from "../images/phAlkaline.svg";

export default function phLevel() {
  const [phlevel, setphlevel] = useState(null);

  useEffect(() => {
    const fetchphlevel = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/phlevel");
        const data = await response.json();
        setphlevel(data.phlevel);
      } catch (error) {
        console.error("Error fetching phlevel data:", error);
      }
    };

    fetchphlevel();

    const interval = setInterval(fetchphlevel, 5000);
    return () => clearInterval(interval);
  }, []);

  const getConditionMessage = () => {
    if (phlevel >= 6 && phlevel <= 7) {
      return "Normal";
    } else if (phlevel < 6 && phlevel >= 5) {
      return "Below Average";
    } else if (phlevel < 5) {
      return "Very Acidic";
    } else if (phlevel > 7 && phlevel <= 9) {
      return "Above Average";
    } else if (phlevel > 9) {
      return "Too High Alkaline";
    } else {
      return "";
    }
  };

  const getpHimage = () => {
    if (phlevel >= 6 && phlevel <= 7) {
      return phAverage;
    } else if (phlevel < 6 && phlevel >= 5) {
      return phBelowAve;
    } else if (phlevel < 5) {
      return phAcid;
    } else if (phlevel > 7 && phlevel <= 9) {
      return phAboveAve;
    } else if (phlevel > 9) {
      return phAlka;
    }
  };

  const getLineColor = () => {
    if (phlevel >= 6 && phlevel <= 7) {
      return "bg-[#24ae24]";
    } else if (phlevel < 6 && phlevel >= 5) {
      return "bg-[#ffd966]";
    } else if (phlevel < 5) {
      return "bg-orange-500";
    } else if (phlevel > 7 && phlevel <= 9) {
      return "bg-[#38eeff]";
    } else if (phlevel > 9) {
      return "bg-[#800080]";
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
          <div className="font-bold text-2xl text-black">pH Level</div>
          <img className="w-8 h-8" src={getpHimage()} alt="Logo" />
        </div>
        <div className="flex justify-end mb-2 mt-4">
          <div>
            <div className="flex justify-end">
              <p className="text-black font-semibold text-3xl mb-1">
                {phlevel ? `${phlevel} pH` : "NAN"}
              </p>
            </div>
            <p className="text-black font-medium text-2xl">
              {phlevel ? getConditionMessage() : ""}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
