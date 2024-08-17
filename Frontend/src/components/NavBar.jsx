import RTU from "../images/rtu logo.png";
import Logout from "./Logout";

export default function NavBar() {
  return (
    <div className="">
      <div className="flex h-24 w-screen bg-gradient-to-r from-[#0AD1C8] to-[#213A57] rounded-b-lg shadow-xl">
        <div className="flex items-center">
          <div className="flex flex-row items-center mx-11">
            <img className="w-20 h-20" src={RTU} alt="Logo" />
            
              <p className=" font-semibold text-white text-4xl pl-4 pr-2"> AUTOAQUAMANS</p>

          </div>
        </div>
        <div className="flex flex-row items-center flex-grow">
          <button className="text-white font-medium text-xl hover:text-[#0b6477] mr-4">
            <p className="pr-2">Home</p>
          </button>
          <button className="text-white font-medium text-xl hover:text-[#0b6477] mr-4">
            <p className="pr-2">Dashboard</p>
          </button>
          <button className="text-white font-medium text-xl hover:text-[#0b6477]">
            <p className="pr-2">Live Monitoring</p>
          </button>

          <div className="flex flex-grow justify-end px-5">
            <button className="text-white font-medium text-xl hover:text-[#0b6477] pr-2">
              <p className="pr-2">About Us</p>
            </button>
            <Logout />
          </div>
        </div>
      </div>
    </div>
  );
}
