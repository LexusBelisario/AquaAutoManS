import React, { useEffect, useState } from "react";
import Navbar from "../components/NavBar";
import Sidebar from "../components/sideBar";
import Turbidity from "../components/turbidityy";
import Temperature from "../components/temp";
import Oxygen from "../components/oxygenn";
import PhLevel from "../components/phLevel";
import AliveCatfish from "../components/aliveCatfish";
import DeadCatfish from "../components/deadCatfish";
import AlertBox from "../components/alertBox";
import LiveMonitoring from "../pages/LiveMonitoring";
import { LineGraphTemp } from "../graphs/lineGraphTemp";
import { LineGraphOxygen } from "../graphs/lineGraphOxy";
import { LineGraphPH } from "../graphs/lineGraphPH";
import axios from "axios";

export default function Homepage({ setAuth }) {
  const [alerts, setAlerts] = useState([]);
  const [catfishCounts, setCatfishCounts] = useState({ alive: 0, dead: 0 });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:5000/data");
        const data = response.data;
        updateCatfishCounts(data);
        checkWaterConditions(data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 5000);
    return () => clearInterval(intervalId);
  }, []);

  const updateCatfishCounts = (data) => {
    if (data.length > 0) {
      const latestRow = data[data.length - 1];
      setCatfishCounts({
        alive: latestRow.catfish,
        dead: latestRow.dead_catfish,
      });
    } else {
      setCatfishCounts({ alive: 0, dead: 0 });
    }
  };

  const checkWaterConditions = (data) => {
    let messages = [];

    if (data.length > 0) {
      const latestRow = data[data.length - 1];

      if (latestRow.temperature < 20) {
        messages.push("The temperature is too low. Please change the water.");
      } else if (latestRow.temperature > 35) {
        messages.push("The temperature is too high. Please change the water.");
      }

      if (latestRow.oxygen < 1) {
        messages.push("The oxygen level is too low. Please change the water.");
      } else if (latestRow.oxygen > 10) {
        messages.push("The oxygen level is too high. Please change the water.");
      }

      if (latestRow.phlevel < 6 && latestRow.phlevel >= 5) {
        messages.push("The pH level is too low. Please change the water.");
      } else if (latestRow.phlevel > 7) {
        messages.push("The pH level is too high. Please change the water.");
      }

      if (latestRow.turbidity >= 30) {
        messages.push("The water is cloudy. Please change the water.");
      }
      if (latestRow.turbidity >= 50) {
        messages.push("The water is too dirty, Change the water Immediately!");
      }

      // Check catfish detection
      if (latestRow.catfish === 0 && latestRow.dead_catfish === 0) {
        messages.push("No catfish detected in the system.");
      } else {
        if (latestRow.catfish > 0) {
          messages.push(`${latestRow.catfish} alive catfish detected.`);
        }
        if (latestRow.dead_catfish > 0) {
          messages.push(`${latestRow.dead_catfish} dead catfish detected.`);
        }
      }

      setAlerts(messages);
    } else {
      setAlerts(["No data available."]);
    }
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
            </div>
          </div>

          {/* Alert Box */}
          <div>
            <p className="text-2xl font-bold mb-4">Alert Notifications</p>
            <AlertBox alerts={alerts} />
          </div>

          {/* Graph Components */}
          <div className="flex flex-col items-start">
            <p className="text-2xl font-bold mb-8">Graphs</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-16 w-full">
              <LineGraphTemp />
              <LineGraphOxygen />
              <LineGraphPH />
            </div>
          </div>

          {/* Live Monitoring Feed */}
          <div>
            {" "}
            <p className="text-2xl font-bold mb-8">Live Monitoring</p>
            <div className="min-h-screen bg-[#F0F8FF] overflow-hidden">
              <LiveMonitoring />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
