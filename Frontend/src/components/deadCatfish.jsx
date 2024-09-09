import React from "react";
import deadfish from "../images/deadFish.svg";

export default function aliveCatfish() {
  return (
    <div className="bg-slate-50 rounded-md border p-4 border-gray-100 shadow-md h-40 w-72 relative">
      <div className="absolute top-0 left-0 h-full w-2 bg-red-800 rounded-tl-md rounded-bl-md"></div>
      <div className="ml-2 pl-2">
        <div className="flex justify-between">
          <div className="font-bold text-2xl text-black">Dead Catfish</div>
          <img className="w-8 h-8" src={deadfish} alt="ded Pic" />
        </div>
        <div className="flex justify-end mt-2">
          <div>
            <div className="flex justify-end mt-2">
              <p className="text-black font-semibold text-4xl">2</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
