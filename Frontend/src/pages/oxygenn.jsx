import React, { useEffect, useState } from 'react';
import oxy from "../images/oxygImg.svg"

export default function oxygenn() {

  const [oxygen, setOxygen] = useState(null);


useEffect(() => {
    const fetchOxygen = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/oxygen"); // Update the URL to your Flask API endpoint
        const data = await response.json();
        setOxygen(data.oxygen);
      } catch (error) {
        console.error("Error fetching oxygen data:", error);
      }
    };

    fetchOxygen();

    const interval = setInterval(fetchOxygen, 5000); // Fetch new data every 5 seconds
    return () => clearInterval(interval); // Cleanup the interval on component unmount
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
      return "NAN";
    }
  };

  return (
    <div className='bg-[#7EABA2] rounded-md border p-4 border-gray-100 shadow-md shadow-black/5 h-64 w-96'>
    <div className='flex mb-4'>
        <div>
            <div className='flex items-center mb-10'>
            <img className="w-8 h-8" src={oxy} alt="Logo" />
                <div className='font-semibold text-4xl text-white ml-4'>Oxygen</div>
            </div>
            <div>
            <div className=''>
            <p className='text-white font-semibold text-6xl mb-1'>{oxygen ? `${oxygen} mg/l` : "NAN"}</p>
            <p className='text-white font-semibold text-4xl'>{oxygen ? getOxygenConditionMessage() : ""}</p>


                </div>
            </div>
        </div>
    </div>
</div>

  )
}
