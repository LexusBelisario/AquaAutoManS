import RTU from "../images/rtu logo.png";
import Logout from "./Logout";

export default function NavBar() {
  return (
    <div className="flex flex-col">
      <div className="flex h-28 w-screen bg-gradient-to-r from-[#657d82] to-[#FA8072] rounded-b-lg shadow-xl">
        <div className="flex items-center mx-6">
          <div className="flex flex-row items-center">
            <img className=" w-20 h-20" src={RTU} />
            <p className=" ml-4 font-semibold text-white text-4xl">
              AutoAquaManS
            </p>
          </div>
        </div>
        <div className="flex flex-row">
          <button className="text-white font-medium text-xl hover:text-purple-500">
            <p className=" pr-2">Home</p>
          </button>
          <button className="text-white font-medium text-xl hover:text-purple-500">
            <p className=" pr-2">Water Turbidity Chart</p>
          </button>
          <button className="text-white font-medium text-xl hover:text-purple-500">
            <p className=" pr-2">Water Temperature Chart</p>
          </button>
          <button className="text-white font-medium text-xl hover:text-purple-500">
            <p className=" pr-2">Water pH Level Chart</p>
          </button>
          <button className="text-white font-medium text-xl hover:text-purple-500">
            <p className=" pr-2">Monitoring</p>
          </button>
          <Logout />
        </div>
      </div>
    </div>
  );
}
