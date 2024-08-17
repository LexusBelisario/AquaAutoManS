import React from 'react'
import turbs from "../images/turbImg.svg"

export default function turbidity() {
  return (
    <div className='bg-[#74CCF4] rounded-md border p-4 border-gray-100 shadow-md shadow-black/5 h-64 w-96'>
    <div className='flex mb-4'>
        <div>
            <div className='flex items-center mb-10'>
            <img className="w-8 h-8" src={turbs} alt="Logo" />
                <div className='font-semibold text-4xl text-white ml-4'>Water Turbidity</div>
            </div>
            <div>
            <div className='flex justify-end'><p className='text-white font-semibold text-8xl mb-1'>23</p></div>
            <div className='flex justify-end'><p className='text-white font-semibold text-4xl'>Clean</p></div>
            </div>
        </div>
    </div>
</div>

  )
}
