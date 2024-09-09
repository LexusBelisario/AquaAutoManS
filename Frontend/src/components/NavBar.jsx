import React from "react";
import { useNavigate } from "react-router-dom";
import RTU from "../images/rtu logo.png";
import Logout from "./Logout";

export default function NavBar({ setAuth }) {
  const navigate = useNavigate();

  const handleLogsClick = () => {
    navigate("/logs");
  };

  const handleHomeClick = () => {
    navigate("/main");
  };

  return (
    <div className="flex h-16 w-full bg-[#28282B]">
      <div className="flex items-center">
        <div className="flex flex-row items-center mx-11">
          <img className="w-10 h-15" src={RTU} alt="Logo" />
          <p className="font-semibold text-white text-2xl pl-4 pr-2">
            AUTOAQUAMANS
          </p>
        </div>
      </div>
      {/* <div className="flex flex-row items-center flex-grow">
        <button
          className="text-white font-medium text-xl hover:text-[#0b6477] mr-4"
          onClick={handleHomeClick}
        >
          <p className="pr-2">Dashboard</p>
        </button>
        <button
          className="text-white font-medium text-xl hover:text-[#0b6477] mr-4"
          onClick={handleLogsClick} // Add onClick handler
        >
          <p className="pr-2">Logs</p>
        </button>
        <div className="flex flex-grow justify-end px-5">
          <button className="text-white font-medium text-xl hover:text-[#08ED99] pr-2">
            <p className="pr-2">About Us</p>
          </button>
          <button className="text-white font-medium text-xl hover:text-[#08ED99] pl-2">
            <p className="pr-2">Send Feedback</p>
          </button>
          <Logout setAuth={setAuth} />
        </div>
      </div> */}
    </div>
  );
}
