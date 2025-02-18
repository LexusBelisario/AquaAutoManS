import React, { useEffect, useState } from "react";
import fish from "../images/fishCat.svg";

export default function AliveCatfish() {
  const [aliveCount, setAliveCount] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAliveCount = async () => {
      try {
        const response = await fetch("http://localhost:5000/catfish");
        const data = await response.json();
        if (data.status === 'success') {
          setAliveCount(data.catfish || 0);
          setError(null);
        } else {
          setError('Failed to fetch data');
        }
      } catch (error) {
        console.error("Error fetching alive catfish count:", error);
        setError('Failed to fetch data');
      }
    };

    fetchAliveCount();
    const interval = setInterval(fetchAliveCount, 2000);

    return () => clearInterval(interval);
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
          {error ? (
            <p className="text-red-500 text-sm">Error loading data</p>
          ) : (
            <p className="text-black font-semibold text-4xl">{aliveCount}</p>
          )}
        </div>
      </div>
    </div>
  );
}