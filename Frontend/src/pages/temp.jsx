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

  const getTemperatureStatus = () => {
    if (temperature >= 26 && temperature <= 32) {
      return "Normal";
    } else if (temperature < 26 && temperature > 20) {
      return "Below Average";
    } else if (temperature <= 20) {
      return "Too Cold!";
    } else if (temperature > 26 && temperature < 35) {
      return "Above Average";
    } else if (temperature >= 35) {
      return "Too Hot!";
    }
  };

  return (
    <div className='bg-[#EE6600] rounded-md border p-4 border-gray-100 shadow-md shadow-black/5 h-64 w-96'>
      <div className='flex mb-4'>
        <div>
          <div className='flex items-center mb-10'>
            <img className="w-8 h-8" src={temps} alt="Logo" />
            <div className='font-semibold text-4xl text-white ml-4'>Temperature</div>
          </div>
          <div>
            <div>
              <p className='text-white font-semibold text-6xl mb-6'>{temperature ? `${temperature}°C` : "NAN"}</p>
              <p className='text-white font-semibold text-4xl'>
              { getTemperatureStatus()}
              {/* {temperature !== null ? `The water temperature is ${getTemperatureStatus()}` : ""} */}
            </p>

            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
