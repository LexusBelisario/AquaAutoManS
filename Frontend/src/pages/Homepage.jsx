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
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import ErrorBoundary from "../components/ErrorBoundary";

const API_URL = "http://localhost:5000/api/water-quality";

export default function Homepage({ setAuth }) {
  const [deadCatfishAlerts, setDeadCatfishAlerts] = useState([]);
  const [waterQualityAlerts, setWaterQualityAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Notification function
  const notifyWaterQualityIssue = (alert) => {
    const priority = determineAlertPriority(alert);
    const toastOptions = {
      position: "top-right",
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
    };

    switch (priority) {
      case "Critical":
        toast.error(`Critical Alert: ${getAlertMessage(alert)}`, toastOptions);
        break;
      case "Warning":
        toast.warning(`Warning: ${getAlertMessage(alert)}`, toastOptions);
        break;
      default:
        toast.info(`Water quality update`, toastOptions);
    }
  };

  const determineAlertPriority = (data) => {
    if (
      data.tempResult === "Critical" ||
      data.oxygenResult === "Critical" ||
      data.phResult === "Critical" ||
      data.turbidityResult === "Critical"
    ) {
      return "Critical";
    }
    if (
      data.tempResult === "Warning" ||
      data.oxygenResult === "Warning" ||
      data.phResult === "Warning" ||
      data.turbidityResult === "Warning"
    ) {
      return "Warning";
    }
    return "Normal";
  };

  const getAlertMessage = (data) => {
    const issues = [];
    if (data.tempResult !== "Normal")
      issues.push(`Temperature is ${data.tempResult.toLowerCase()}`);
    if (data.oxygenResult !== "Normal")
      issues.push(`Oxygen is ${data.oxygenResult.toLowerCase()}`);
    if (data.phResult !== "Normal")
      issues.push(`pH is ${data.phResult.toLowerCase()}`);
    if (data.turbidityResult !== "Normal")
      issues.push(`Turbidity is ${data.turbidityResult.toLowerCase()}`);
    return issues.join(", ") || "All parameters need attention";
  };

  // Fetch water quality data
  useEffect(() => {
    const fetchWaterQuality = async () => {
      try {
        const response = await axios.get(`${API_URL}/check`);
        console.log("Raw API response:", response.data);

        if (response.data && response.data.alert_id) {
          const formattedAlert = {
            alert: "Water Quality Status Update",
            details: {
              alert_id: response.data.alert_id,
              time_detected: response.data.time_detected,
              priority_level: determineAlertPriority(response.data),

              temperature: response.data.temperature,
              temperature_status: response.data.tempResult,
              temperature_trend: response.data.temperature_trend,
              temperature_history: response.data.historical_data.temperature,

              oxygen: response.data.oxygen,
              oxygen_status: response.data.oxygenResult,
              oxygen_trend: response.data.oxygen_trend,
              oxygen_history: response.data.historical_data.oxygen,

              phlevel: response.data.phlevel,
              phlevel_status: response.data.phResult,
              ph_trend: response.data.ph_trend,
              ph_history: response.data.historical_data.ph,

              turbidity: response.data.turbidity,
              turbidity_status: response.data.turbidityResult,
              turbidity_trend: response.data.turbidity_trend,
              turbidity_history: response.data.historical_data.turbidity,

              detected_issues: [getAlertMessage(response.data)],
              recommendations: generateRecommendations(response.data),
            },
          };

          console.log("Formatted alert:", formattedAlert);

          setWaterQualityAlerts((prevAlerts) => {
            const newAlerts = [...prevAlerts];
            const existingAlertIndex = newAlerts.findIndex(
              (alert) =>
                alert.details.alert_id === formattedAlert.details.alert_id
            );

            if (existingAlertIndex === -1) {
              newAlerts.unshift(formattedAlert);
            } else {
              newAlerts[existingAlertIndex] = formattedAlert;
            }

            return newAlerts.slice(0, 5); // Keep only last 5 alerts
          });

          if (formattedAlert.details.priority_level !== "Normal") {
            notifyWaterQualityIssue(response.data);
          }
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
      <ToastContainer />

      {/* Navbar with Notifications */}
      <div className="fixed top-0 left-0 right-0 z-50">
        <div className="flex justify-between items-center bg-white shadow">
          <Navbar />
          <div className="mr-4">
            <ErrorBoundary>
              <WaterQualityAlertBox
                alerts={waterQualityAlerts}
                removeAlert={removeWaterQualityAlert}
              />
            </ErrorBoundary>
          </div>
        </div>
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

function generateRecommendations(data) {
  const recommendations = [];

  if (data.tempResult !== "Normal") {
    recommendations.push(
      data.temperature > 32
        ? "Activate cooling system and increase water circulation"
        : "Check heater functionality and monitor water temperature"
    );
  }

  if (data.oxygenResult !== "Normal") {
    recommendations.push(
      data.oxygen < 5
        ? "Increase aeration and check oxygen supply system"
        : "Monitor oxygen levels and adjust aeration accordingly"
    );
  }

  if (data.phResult !== "Normal") {
    recommendations.push(
      "Check pH levels and adjust water chemistry as needed"
    );
  }

  if (data.turbidityResult !== "Normal") {
    recommendations.push(
      "Check filtration system and consider partial water change"
    );
  }

  return recommendations;
}
