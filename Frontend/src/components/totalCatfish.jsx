import React, { useEffect, useState } from "react";
import fish from "../images/fishCat.svg";

export default function TotalCatfish() {
  const [totalCatfish, setTotalCatfish] = useState(0);

  useEffect(() => {
    const fetchTotalCatfish = async () => {
      try {
        const response = await fetch("http://localhost:5000/data");
        const data = await response.json();
        const latestRecord = data[data.length - 1];

        const total =
          (latestRecord.catfish || 0) + (latestRecord.dead_catfish || 0);
        setTotalCatfish(total);
      } catch (error) {
        console.error("Error fetching total catfish count:", error);
      }
    };

    fetchTotalCatfish();
    const interval = setInterval(fetchTotalCatfish, 2000);

    return () => clearInterval(interval); // Cleanup on component unmount
  }, []);

  return (
    <div className="bg-slate-50 rounded-md border p-4 border-gray-100 shadow-md h-40 w-72 relative">
      <div className="absolute top-0 left-0 h-full w-2 bg-[#84979b] rounded-tl-md rounded-bl-md"></div>
      <div className="ml-2 pl-2">
        <div className="flex justify-between">
          <div className="font-bold text-2xl text-black">Total Catfish</div>
          <img className="w-8 h-8" src={fish} alt="Catfish Pic" />
        </div>
        <div className="flex justify-end mt-2">
          <p className="text-black font-semibold text-4xl">{totalCatfish}</p>
        </div>
      </div>
    </div>
  );
}
