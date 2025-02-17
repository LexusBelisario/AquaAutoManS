import React, { useEffect, useState } from "react";
import Navbar from "../components/NavBar";
import Sidebar from "../components/sideBar";
import Turbidity from "../components/turbidityy";
import Temperature from "../components/temp";
import Oxygen from "../components/oxygenn";
import PhLevel from "../components/phLevel";
import AliveCatfish from "../components/aliveCatfish";
import DeadCatfish from "../components/deadCatfish";
import TotalCatfish from "../components/totalCatfish";
import AlertBox from "../components/alertBox";
import PictureBox from "../components/pictureBox";
import { LineGraphTemp } from "../graphs/lineGraphTemp";
import { LineGraphOxygen } from "../graphs/lineGraphOxy";
import { LineGraphPH } from "../graphs/lineGraphPH";
import { LineGraphTurb } from "../graphs/lineGraphTurb";
import axios from "axios";

export default function Homepage({ setAuth }) {
  const [alerts, setAlerts] = useState([]);
  const [catfishCounts, setCatfishCounts] = useState({ alive: 0, dead: 0 });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          "http://localhost:5000/check_dead_catfish"
        );

        if (response.data.alert) {
          setAlerts((prevAlerts) => {
            const newAlert = {
              message: response.data.alert,
              details: response.data.details,
            };
            return prevAlerts.some(
              (alert) => alert.message === newAlert.message
            )
              ? prevAlerts
              : [...prevAlerts, newAlert];
          });
        }
      } catch (error) {
        console.error("Error fetching dead catfish alert:", error);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 2000);
    return () => clearInterval(intervalId);
  }, []);
  const removeAlert = (index) => {
    setAlerts((prevAlerts) => prevAlerts.filter((_, i) => i !== index));
  };

  return (
    <div className="min-h-screen bg-[#F0F8FF] overflow-hidden">
      {/* Navbar */}
      <div className="fixed top-0 left-0 right-0 z-50">
        <Navbar />
      </div>

      {/* Main content container */}
      <div className="flex mt-16">
        {/* Sidebar */}
        <div className="fixed">
          <Sidebar setAuth={setAuth} />
        </div>

        {/* Main content */}
        <div className="flex-1 flex flex-col ml-64 p-4 space-y-10">
          {/* Dashboard Components */}
          <div className="flex flex-col items-start">
            <p className=" text-2xl font-bold mb-2">Dashboard</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-36">
              <Temperature />
              <Oxygen />
              <PhLevel />
              <Turbidity />
            </div>
          </div>

          {/* Catfish Components */}
          <div className="flex flex-col items-start">
            <p className="text-2xl font-bold">Catfish Detection</p>
            <div className="flex flex-wrap justify-start space-x-10 my-5 gap-28">
              <AliveCatfish />
              <DeadCatfish />
              <TotalCatfish />
            </div>
          </div>

          {/* Alert Box */}
          <div>
            <p className="text-2xl font-bold mb-4">Alert Notifications</p>
            <AlertBox alerts={alerts} removeAlert={removeAlert} />
            <p className="text-2xl font-bold my-4">Image Notifications</p>
            <PictureBox />
          </div>

          {/* Graph Components */}
          <div className="flex flex-col items-start">
            <p className="text-2xl font-bold mb-8">Graphs</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-16 w-full">
              <LineGraphTemp />
              <LineGraphOxygen />
              <LineGraphPH />
              <LineGraphTurb />
            </div>
          </div>

          {/* Live Monitoring Feed */}
          <div>
            {" "}
            <p className="text-2xl font-bold mb-8">Live Monitoring</p>
            <div className="min-h-screen bg-[#F0F8FF] overflow-hidden">
              sdsd
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}