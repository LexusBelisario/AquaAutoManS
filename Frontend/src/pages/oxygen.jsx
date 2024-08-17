import React from 'react'
import oxy from "../images/oxygImg.svg"

export default function oxygen() {
  return (
    <div className='bg-[#7EABA2] rounded-md border p-4 border-gray-100 shadow-md shadow-black/5 h-64 w-96'>
    <div className='flex mb-4'>
        <div>
            <div className='flex items-center mb-10'>
            <img className="w-8 h-8" src={oxy} alt="Logo" />
                <div className='font-semibold text-4xl text-white ml-4'>Oxygen</div>
            </div>
            <div>
            <div className='flex justify-end'>
                <p className='text-white font-semibold text-7xl mb-1'>2.2</p>
                <p className='text-white font-semibold text-7xl mb-1'>mg/l</p>

                </div>
            </div>
        </div>
    </div>
</div>

  )
}
