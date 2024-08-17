import React from 'react'
import phil from "../images/phLvel.svg"

export default function temp() {
  return (
    <div className='bg-[#37A737] rounded-md border p-4 border-gray-100 shadow-md shadow-black/5 h-64 w-96'>
    <div className='flex mb-4'>
        <div>
            <div className='flex items-center mb-10'>
            <img className="w-8 h-8" src={phil} alt="Logo" />
                <div className='font-semibold text-4xl text-white ml-4'>pH Level</div>
            </div>
            <div>
            <div className='flex justify-end'><p className='text-white font-semibold text-8xl mb-1'>2</p></div>
            <div className='flex justify-end'><p className='text-white font-semibold text-4xl'></p></div>
            </div>
        </div>
    </div>
</div>

  )
}
