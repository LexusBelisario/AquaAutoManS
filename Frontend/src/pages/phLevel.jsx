import React, { useEffect, useState } from 'react';
import phil from "../images/phLvel.svg"

export default function phLevel()
{
  const [phlevel, setphlevel] = useState(null);


useEffect(() => {
    const fetchphlevel = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/phlevel"); // Update the URL to your Flask API endpoint
        const data = await response.json();
        setphlevel(data.phlevel);
      } catch (error) {
        console.error("Error fetching phlevel data:", error);
      }
    };

    fetchphlevel();

    const interval = setInterval(fetchphlevel, 5000); // Fetch new data every 5 seconds
    return () => clearInterval(interval); // Cleanup the interval on component unmount
  }, []);

  const getConditionMessage = () => {
    if (phlevel >= 6 && phlevel <= 7) {
      return "Normal";
    } else if (phlevel < 6 && phlevel >= 5) {
      return "Below Average";
    } else if (phlevel < 5) {
      return "Too Acidic";
    } else if (phlevel > 7 && phlevel <= 9) {
      return "Above Average";
    } else if (phlevel > 9) {
      return "Too High Alkaline";
    } else {
      return "NAN";
    }
  };

  return (
    <div className='bg-[#37A737] rounded-md border p-4 border-gray-100 shadow-md shadow-black/5 h-64 w-96'>
    <div className='flex mb-4'>
        <div>
            <div className='flex items-center mb-10'>
            <img className="w-8 h-8" src={phil} alt="Logo" />
                <div className='font-semibold text-4xl text-white ml-4'>pH Level</div>
            </div>
            <div>
            <p className='text-white font-semibold text-6xl mb-1'>{phlevel ? `${phlevel} pH` : "NAN"}</p>
            <p className='text-white font-semibold text-4xl'>{phlevel ? getConditionMessage() : ""}</p>
            </div>
        </div>
    </div>
</div>

  )
}
