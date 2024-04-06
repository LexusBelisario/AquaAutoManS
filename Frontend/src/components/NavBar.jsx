import RTU from "../images/rtu logo.png";
import Logout from "./Logout";

export default function NavBar() {
  return (
    <div className="">
      <div className="flex h-28 w-screen bg-gradient-to-r from-[#657d82] to-[#FA8072] rounded-b-lg shadow-xl">
        <div className="flex items-center mx-6">
          <div className="flex flex-row items-center">
            <img className="w-20 h-20" src={RTU} alt="Logo" />
            <button className="ml-4 font-semibold text-white text-4xl hover:text-purple-500 mr-4">
              <p className="pr-2"> AutoAquaManS</p>
            </button>
          </div>
        </div>
        <div className="flex flex-row items-center flex-grow px-14">
          <button className="text-white font-medium text-xl hover:text-purple-500 mr-4">
            <p className="pr-2">Water Turbidity Chart</p>
          </button>
          <button className="text-white font-medium text-xl hover:text-purple-500 mr-4">
            <p className="pr-2">Water Temperature Chart</p>
          </button>
          <button className="text-white font-medium text-xl hover:text-purple-500 mr-4">
            <p className="pr-2">Water pH Level Chart</p>
          </button>
          <button className="text-white font-medium text-xl hover:text-purple-500 mr-4">
            <p className="pr-2">Monitoring</p>
          </button>
          <div className="flex flex-grow justify-end px-5">
            <Logout />
          </div>
        </div>
      </div>
    </div>
  );
}
