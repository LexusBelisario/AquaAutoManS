import React from "react";
import Navbar from "../components/NavBar";
import Sidebar from "../components/sideBar";
import Turbidity from "../components/turbidityy";
import Temperature from "../components/temp";
import Oxygen from "../components/oxygenn";
import PhLevel from "../components/phLevel";
import AliveCatfish from "../components/aliveCatfish";
import DeadCatfish from "../components/deadCatfish";

export default function Homepage({ setAuth }) {
  return (
    <div className="min-h-screen bg-[#F0F8FF] overflow-hidden overflow-x-hidden">
      <Navbar setAuth={setAuth} />

      {/* Main content container */}
      <div className="flex">
        <div className="fixed">
          {" "}
          <Sidebar setAuth={setAuth} />
        </div>

        <div className="flex-1 flex flex-wrap justify-center items-start mt-8 space-x-10 px-4">
          <div>
            <Temperature />
          </div>
          <div>
            <Oxygen />
          </div>
          <div>
            <PhLevel />
          </div>
          <div>
            <Turbidity />
          </div>
        </div>
      </div>
      <div className="flex flex-wrap justify-center space-x-10 my-5">
        {" "}
        <div>
          <AliveCatfish />
        </div>
        <div>
          <DeadCatfish />
        </div>
      </div>
    </div>
  );
}
