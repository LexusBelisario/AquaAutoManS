import React, { useEffect, useState } from 'react';
import temps from "../images/tempImg.svg"

export default function Temp() {
  const [temperature, setTemperature] = useState(null);

  useEffect(() => {
    const fetchTemperature = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/temperature"); // Update the URL to your Flask API endpoint
        const data = await response.json();
        setTemperature(data.temperature);
      } catch (error) {
        console.error("Error fetching temperature data:", error);
      }
    };

    fetchTemperature();

    const interval = setInterval(fetchTemperature, 5000); // Fetch new data every 5 seconds
    return () => clearInterval(interval); // Cleanup the interval on component unmount
  }, []);

  return (
    <div className='bg-[#EE6600] rounded-md border p-4 border-gray-100 shadow-md shadow-black/5 h-64 w-96'>
      <div className='flex mb-4'>
        <div>
          <div className='flex items-center mb-10'>
            <img className="w-8 h-8" src={temps} alt="Logo" />
            <div className='font-semibold text-4xl text-white ml-4'>Temperature</div>
          </div>
          <div>
            <div className='flex justify-end'>
              <p className='text-white font-semibold text-8xl mb-1'>{temperature ? `${temperature}°C` : "NAN"}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
