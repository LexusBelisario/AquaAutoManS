import React, { useEffect, useState } from "react";
import fish from "../images/fishCat.svg";

export default function AliveCatfish() {
  const [catfishCount, setCatfishCount] = useState(0);

  useEffect(() => {
    fetch("http://localhost:5000/catfish")
      .then((response) => response.json())
      .then((data) => {
        setCatfishCount(data.catfish || 0);
      })
      .catch((error) => console.error("Error fetching catfish count:", error));
  }, []);

  return (
    <div className="bg-slate-50 rounded-md border p-4 border-gray-100 shadow-md h-40 w-72 relative">
      <div className="absolute top-0 left-0 h-full w-2 bg-[#5f4d4d] rounded-tl-md rounded-bl-md"></div>
      <div className="ml-2 pl-2">
        <div className="flex justify-between">
          <div className="font-bold text-2xl text-black">Alive Catfish</div>
          <img className="w-8 h-8" src={fish} alt="Alive Pic" />
        </div>
        <div className="flex justify-end mt-2">
          <p className="text-black font-semibold text-4xl">{catfishCount}</p>
        </div>
      </div>
    </div>
  );
}
