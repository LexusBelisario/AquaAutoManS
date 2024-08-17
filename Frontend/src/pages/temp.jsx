import React from 'react'
import temps from "../images/tempImg.svg"

export default function temp() {
  return (
    <div className='bg-[#EE6600] rounded-md border p-4 border-gray-100 shadow-md shadow-black/5 h-64 w-96'>
    <div className='flex mb-4'>
        <div>
            <div className='flex items-center mb-10'>
            <img className="w-8 h-8" src={temps} alt="Logo" />
                <div className='font-semibold text-4xl text-white ml-4'>Temperature</div>
            </div>
            <div>
            <div className='flex justify-end'><p className='text-white font-semibold text-8xl mb-1'>32°C</p></div>
            <div className='flex justify-end'><p className='text-white font-semibold text-4xl'></p></div>
            </div>
        </div>
    </div>
</div>

  )
}
