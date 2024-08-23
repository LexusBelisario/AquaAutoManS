import React, { useEffect, useState } from 'react';
import turbs from "../images/turbImg.svg"

export default function turbidityy() {

  const [turbidity, setTurbidity] = useState(null);

  useEffect(() => {
    const fetchTurbidity= async () => {
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
    } else if (turbidity >=50){
      return "Dirty";
    } else if (turbidity <=60){
      return "Super Dirty";
    }
  };

  

  return (
    <div className='bg-[#74CCF4] rounded-md border p-4 border-gray-100 shadow-md shadow-black/5 h-64 w-96'>
    <div className='flex mb-4'>
        <div>
            <div className='flex items-center mb-10'>
            <img className="w-8 h-8" src={turbs} alt="Logo" />
                <div className='font-semibold text-4xl text-white ml-4'>Water Turbidity</div>
            </div>
            <div>
            <p className='text-white font-semibold text-6xl mb-1'>{turbidity ? `${turbidity} V ` : "NAN"}</p>
            <p className='text-white font-semibold text-3xl'> {turbidity !== null ? `The water is ${getTurbidityStatus()}` : ""}</p>
            
             </div>
        </div>
    </div>
</div>

  )
}
