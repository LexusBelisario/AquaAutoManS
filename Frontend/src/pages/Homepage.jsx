import React from "react";
import Navbar from "../components/NavBar";
import Sidebar from "../components/sideBar";
import Turbidity from "../components/turbidityy";
import Temperature from "../components/temp";
import Oxygen from "../components/oxygenn";
import PhLevel from "../components/phLevel";
import AliveCatfish from "../components/aliveCatfish";
import DeadCatfish from "../components/deadCatfish";
import { LineGraphTemp } from "../graphs/lineGraphTemp";

export default function Homepage({ setAuth }) {
  return (
    <div className="min-h-screen bg-[#F0F8FF] overflow-hidden">
      {/* Fixed Navbar */}
      <div className="fixed top-0 left-0 right-0 z-50">
        <Navbar />
      </div>

      {/* Main content container */}
      <div className="flex mt-16">
        {/* Fixed Sidebar */}
        <div className="fixed top-16 left-0 z-40">
          <Sidebar setAuth={setAuth} />
        </div>

        {/* Main content area */}
        <div className="flex-1 flex flex-col items-center justify-center ml-48 mt-8 space-y-10 px-4">
          {/* Dashboard components */}
          <div className="flex flex-wrap justify-center items-start space-x-10 px-4">
            <Temperature />
            <Oxygen />
            <PhLevel />
            <Turbidity />
          </div>

          {/* Catfish components */}
          <div className="flex flex-wrap justify-center space-x-10 my-5">
            <AliveCatfish />
            <DeadCatfish />
          </div>
          <div className="w-full max-w-4xl justify-center">
            <LineGraphTemp />
          </div>
        </div>
      </div>
    </div>
  );
}
