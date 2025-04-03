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
const CURRENT_TIMESTAMP = "2025-03-21 04:35:50";
const CURRENT_USER = "LexusBelisario";

const CASE_STYLES = {
  5: {
    bg: "bg-purple-100",
    border: "border-purple-500",
    text: "text-purple-700",
    label: "Emergency",
    description: "Mortality Due to Temperature Changes",
    borderLeft: "border-l-4 border-purple-500",
    badge: "bg-purple-600",
  },
  4: {
    bg: "bg-red-100",
    border: "border-red-500",
    text: "text-red-700",
    label: "Critical",
    description: "Critical Parameter Levels",
    borderLeft: "border-l-4 border-red-500",
    badge: "bg-red-600",
  },
  3: {
    bg: "bg-orange-100",
    border: "border-orange-500",
    text: "text-orange-700",
    label: "High",
    description: "Multiple Parameter Warnings",
    borderLeft: "border-l-4 border-orange-500",
    badge: "bg-orange-500",
  },
  2: {
    bg: "bg-yellow-100",
    border: "border-yellow-500",
    text: "text-yellow-700",
    label: "Medium",
    description: "Single Parameter Warning",
    borderLeft: "border-l-4 border-yellow-500",
    badge: "bg-yellow-500",
  },
  1: {
    bg: "bg-green-100",
    border: "border-green-500",
    text: "text-green-700",
    label: "Normal",
    description: "All Parameters Normal",
    borderLeft: "border-l-4 border-green-500",
    badge: "bg-green-500",
  },
};

export default function Homepage({ setAuth }) {
  const [deadCatfishAlerts, setDeadCatfishAlerts] = useState([]);
  const [waterQualityAlerts, setWaterQualityAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastFetchTime, setLastFetchTime] = useState(CURRENT_TIMESTAMP);

  const determineAlertPriority = (data) => {
    if (data.catfish_death) return "Critical";
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
    return issues.join(", ") || "All parameters within normal range";
  };

  const determineCaseLevel = (data) => {
    if (data.catfish_death) return 5;

    const hasCritical = [
      "tempResult",
      "oxygenResult",
      "phResult",
      "turbidityResult",
    ].some((param) => data[param] === "Critical");
    if (hasCritical) return 4;

    const warningCount = [
      "tempResult",
      "oxygenResult",
      "phResult",
      "turbidityResult",
    ].filter((param) => data[param] === "Warning").length;
    if (warningCount >= 2) return 3;
    if (warningCount === 1) return 2;

    return 1;
  };

  const notifyWaterQualityIssue = (alert) => {
    const priority = determineAlertPriority(alert);
    const caseLevel = determineCaseLevel(alert);
    const caseStyle = CASE_STYLES[caseLevel];

    const toastOptions = {
      position: "top-right",
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      className: caseStyle.bg,
      style: {
        borderLeft: `4px solid ${caseStyle.border.replace("border-", "")}`,
        color: caseStyle.text.replace("text-", ""),
      },
    };

    const message = getAlertMessage(alert);

    switch (priority) {
      case "Critical":
        toast.error(`${caseStyle.label} Alert: ${message}`, toastOptions);
        break;
      case "Warning":
        toast.warning(`${caseStyle.label} Alert: ${message}`, toastOptions);
        break;
      default:
        toast.info(`Status Update: ${message}`, toastOptions);
    }
  };

  useEffect(() => {
    const fetchWaterQuality = async () => {
      try {
        const response = await axios.get(`${API_URL}/check`);

        if (response.data && response.data.alert_id) {
          const caseLevel = determineCaseLevel(response.data);
          const formattedAlert = {
            alert: "Water Quality Status Update",
            details: {
              alert_id: response.data.alert_id,
              time_detected: CURRENT_TIMESTAMP,
              priority_level: determineAlertPriority(response.data),
              reported_by: CURRENT_USER,
              case: {
                number: caseLevel,
                title: CASE_STYLES[caseLevel].label,
                description: CASE_STYLES[caseLevel].description,
                severity: determineAlertPriority(response.data),
              },

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
              recommendations: generateRecommendations(
                response.data,
                caseLevel
              ),
            },
          };

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

            return newAlerts.slice(0, 5);
          });

          if (formattedAlert.details.priority_level !== "Normal") {
            notifyWaterQualityIssue(response.data);
          }

          setLastFetchTime(CURRENT_TIMESTAMP);
        }
      } catch (error) {
        console.error("Error fetching water quality data:", error);
        setError(`Failed to fetch water quality data: ${error.message}`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWaterQuality();
    const intervalId = setInterval(fetchWaterQuality, 5000);
    return () => clearInterval(intervalId);
  }, []);

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
              details: {
                ...response.data.details,
                time_detected: CURRENT_TIMESTAMP,
                reported_by: CURRENT_USER,
              },
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
    const intervalId = setInterval(fetchDeadCatfish, 2000);
    return () => clearInterval(intervalId);
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
        <div className="flex justify-between items-center bg-[#28282B]">
          <Navbar />
          <div className="mr-4">
            <ErrorBoundary>
              <WaterQualityAlertBox
                alerts={waterQualityAlerts}
                removeAlert={removeWaterQualityAlert}
                currentTimestamp={CURRENT_TIMESTAMP}
                currentUser={CURRENT_USER}
                lastFetchTime={lastFetchTime}
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
          {/* Error display */}
          {error && (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4">
              <p className="font-bold">Error</p>
              <p>{error}</p>
            </div>
          )}

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

function generateRecommendations(data, caseLevel) {
  const recommendations = [];
  const timestamp = "2025-03-21 04:35:50";
  const user = "LexusBelisario";

  if (caseLevel === 5) {
    recommendations.push({
      priority: "Critical",
      action: "Emergency Response Required",
      details: [
        "Immediately check water quality parameters",
        "Document catfish mortality incident",
        "Prepare detailed incident report",
        "Contact system administrator",
      ],
      timestamp,
      reported_by: user,
    });
  }

  if (data.tempResult !== "Normal") {
    recommendations.push({
      priority: data.tempResult === "Critical" ? "Critical" : "Medium",
      action: `${
        data.tempResult === "Critical" ? "Urgent: " : ""
      }Adjust Water Temperature`,
      details: [
        `Current temperature: ${data.temperature}°C`,
        data.temperature > 32
          ? "Activate cooling system"
          : "Check heater functionality",
        "Monitor temperature every 30 minutes",
        "Document all temperature changes",
      ],
      timestamp,
      reported_by: user,
    });
  }

  if (data.oxygenResult !== "Normal") {
    recommendations.push({
      priority: data.oxygenResult === "Critical" ? "Critical" : "Medium",
      action: `${
        data.oxygenResult === "Critical" ? "Urgent: " : ""
      }Adjust Oxygen Levels`,
      details: [
        `Current oxygen level: ${data.oxygen} mg/L`,
        "Check aeration system",
        "Monitor oxygen levels frequently",
        "Prepare backup aeration system",
      ],
      timestamp,
      reported_by: user,
    });
  }

  if (data.phResult !== "Normal") {
    recommendations.push({
      priority: data.phResult === "Critical" ? "Critical" : "Medium",
      action: `${
        data.phResult === "Critical" ? "Urgent: " : ""
      }Stabilize pH Levels`,
      details: [
        `Current pH level: ${data.phlevel}`,
        "Check water chemistry",
        "Consider partial water change",
        "Monitor pH levels hourly",
      ],
      timestamp,
      reported_by: user,
    });
  }

  if (data.turbidityResult !== "Normal") {
    recommendations.push({
      priority: data.turbidityResult === "Critical" ? "Critical" : "Medium",
      action: `${
        data.turbidityResult === "Critical" ? "Urgent: " : ""
      }Address Water Clarity`,
      details: [
        `Current turbidity: ${data.turbidity} NTU`,
        "Inspect filtration system",
        "Schedule water change if needed",
        "Check for debris or contamination",
      ],
      timestamp,
      reported_by: user,
    });
  }

  return recommendations;
}
