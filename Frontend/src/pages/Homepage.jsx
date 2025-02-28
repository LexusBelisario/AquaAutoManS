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
import LiveVideoFeed from "./LiveVideoFeed";
import WaterQualityAlertBox from "../components/WaterQualityAlertBox";
import ErrorBoundary from "../components/ErrorBoundary";

export default function Homepage({ setAuth }) {
  const [deadCatfishAlerts, setDeadCatfishAlerts] = useState([]);
  const [waterQualityAlerts, setWaterQualityAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch water quality data
  useEffect(() => {
    const fetchWaterQuality = async () => {
      try {
        const response = await axios.get(
          "http://localhost:5000/check_water_quality"
        );
        if (response.data) {
          setWaterQualityAlerts([response.data]);
        }
      } catch (error) {
        console.error("Error fetching water quality data:", error);
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWaterQuality();
    const waterQualityInterval = setInterval(fetchWaterQuality, 5000);

    return () => clearInterval(waterQualityInterval);
  }, []);

  // Fetch dead catfish data
  useEffect(() => {
    const fetchDeadCatfish = async () => {
      try {
        const response = await axios.get(
          "http://localhost:5000/check_dead_catfish"
        );
        if (response.data.alert) {
          setDeadCatfishAlerts((prevAlerts) => {
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

    fetchDeadCatfish();
    const deadCatfishInterval = setInterval(fetchDeadCatfish, 2000);
    return () => clearInterval(deadCatfishInterval);
  }, []);

  const removeWaterQualityAlert = (alertId) => {
    setWaterQualityAlerts((prevAlerts) =>
      prevAlerts.filter((alert) => alert.details.alert_id !== alertId)
    );
  };

  const removeDeadCatfishAlert = (index) => {
    setDeadCatfishAlerts((prevAlerts) =>
      prevAlerts.filter((_, i) => i !== index)
    );
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
            <p className="text-2xl font-bold mb-2">Dashboard</p>
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
            <ErrorBoundary>
              <WaterQualityAlertBox
                alerts={waterQualityAlerts}
                removeAlert={removeWaterQualityAlert}
              />
            </ErrorBoundary>
            <AlertBox
              alerts={deadCatfishAlerts}
              removeAlert={removeDeadCatfishAlert}
            />
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
            <p className="text-2xl font-bold mb-8">Live Monitoring</p>
            <div className="min-h-screen bg-[#F0F8FF] overflow-hidden">
              <LiveVideoFeed />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
