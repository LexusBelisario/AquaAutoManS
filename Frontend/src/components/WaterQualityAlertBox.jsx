import React, { useEffect, useState, useRef } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// Constants for parameter thresholds
const PARAMETER_THRESHOLDS = {
  temperature: {
    critical_low: 20,
    warning_low: 26,
    normal_low: 26,
    normal_high: 32,
    warning_high: 32,
    critical_high: 35,
    unit: "°C",
  },
  oxygen: {
    critical_low: 0.8,
    warning_low: 1.5,
    normal_low: 1.5,
    normal_high: 5,
    warning_high: 5,
    critical_high: 8,
    unit: "mg/L",
  },
  ph: {
    critical_low: 4,
    warning_low: 6,
    normal_low: 6.5,
    normal_high: 7.5,
    warning_high: 8.5,
    critical_high: 9,
    unit: "",
  },
  turbidity: {
    normal: 20,
    warning: 50,
    critical: 100,
    unit: "NTU",
  },
};

// Priority level styling
const PRIORITY_STYLES = {
  Critical: "bg-red-100 border-red-500 text-red-700",
  Warning: "bg-yellow-100 border-yellow-500 text-yellow-700",
  Normal: "bg-green-100 border-green-500 text-green-700",
};

// Utility functions
const getTrendIcon = (trend) => {
  switch (trend) {
    case "↑":
      return "text-red-500";
    case "↓":
      return "text-blue-500";
    default:
      return "text-gray-500";
  }
};

const getStatusColor = (status) => {
  switch (status?.toLowerCase()) {
    case "critical":
      return "text-red-600 font-bold";
    case "warning":
      return "text-yellow-600";
    case "normal":
      return "text-green-600";
    default:
      return "text-gray-600";
  }
};

// Parameter Card Component
const ParameterCard = ({ name, value, unit, status, trend }) => (
  <div className="bg-white bg-opacity-75 rounded-lg p-3">
    <div className="text-sm font-medium text-gray-500">{name}</div>
    <div className="flex items-center space-x-2">
      <span className="text-lg font-bold">
        {value} {unit}
      </span>
      <span className={getTrendIcon(trend)}>{trend}</span>
    </div>
    <div className={getStatusColor(status)}>{status}</div>
  </div>
);

export default function WaterQualityAlertBox({ alerts = [], removeAlert }) {
  const [showDetails, setShowDetails] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    console.log("Water Quality Alerts:", alerts);
    setIsLoading(false);
  }, [alerts]);

  const criticalCount = alerts.filter(
    (alert) => alert.details?.priority_level === "Critical"
  ).length;
  const warningCount = alerts.filter(
    (alert) => alert.details?.priority_level === "Warning"
  ).length;

  const renderTrendGraph = (data, parameter) => {
    if (!data || !data.datasets || !data.labels) {
      return null;
    }

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
        title: {
          display: true,
          text: `${parameter} Trend`,
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          grid: {
            color: (context) => {
              const thresholds = PARAMETER_THRESHOLDS[parameter.toLowerCase()];
              const value = context.tick.value;
              if (thresholds) {
                if (
                  value === thresholds.normal_low ||
                  value === thresholds.normal_high
                ) {
                  return "rgba(0, 255, 0, 0.2)";
                }
                if (
                  value === thresholds.warning_low ||
                  value === thresholds.warning_high
                ) {
                  return "rgba(255, 165, 0, 0.2)";
                }
              }
              return "rgba(0, 0, 0, 0.1)";
            },
          },
        },
      },
    };

    return <Line options={options} data={data} />;
  };

  if (isLoading) {
    return (
      <div className="relative" ref={dropdownRef}>
        <button className="p-2 text-gray-600">
          <svg className="w-6 h-6 animate-spin" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Notification Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-blue-600 focus:outline-none"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>

        {/* Notification Badge */}
        {criticalCount + warningCount > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 rounded-full bg-red-600">
            {criticalCount + warningCount}
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl z-50 max-h-[80vh] overflow-y-auto">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">
                Water Quality Alerts
              </h3>
              <div className="flex space-x-2">
                {criticalCount > 0 && (
                  <span className="px-2 py-1 text-xs font-semibold text-white bg-red-600 rounded-full">
                    {criticalCount} Critical
                  </span>
                )}
                {warningCount > 0 && (
                  <span className="px-2 py-1 text-xs font-semibold text-white bg-yellow-500 rounded-full">
                    {warningCount} Warning
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Alert List */}
          <div className="divide-y divide-gray-200">
            {alerts.length === 0 ? (
              <div className="px-4 py-3 text-sm text-gray-500">
                No active alerts
              </div>
            ) : (
              alerts.map((alert, index) => (
                <div
                  key={alert.details?.alert_id || index}
                  className={`px-4 py-3 hover:bg-gray-50 ${
                    alert.details?.priority_level === "Critical"
                      ? "border-l-4 border-red-500"
                      : alert.details?.priority_level === "Warning"
                      ? "border-l-4 border-yellow-500"
                      : ""
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {alert.details?.priority_level} Alert
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(
                          alert.details?.time_detected
                        ).toLocaleString()}
                      </p>
                    </div>
                    <button
                      onClick={() => removeAlert(alert.details?.alert_id)}
                      className="text-gray-400 hover:text-red-500"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </button>
                  </div>

                  {/* Parameter Summary */}
                  <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="font-medium">Temperature:</span>{" "}
                      {alert.details?.temperature}°C (
                      {alert.details?.temperature_status})
                    </div>
                    <div>
                      <span className="font-medium">Oxygen:</span>{" "}
                      {alert.details?.oxygen} mg/L (
                      {alert.details?.oxygen_status})
                    </div>
                    <div>
                      <span className="font-medium">pH:</span>{" "}
                      {alert.details?.phlevel} ({alert.details?.phlevel_status})
                    </div>
                    <div>
                      <span className="font-medium">Turbidity:</span>{" "}
                      {alert.details?.turbidity} NTU (
                      {alert.details?.turbidity_status})
                    </div>
                  </div>

                  {/* View Details Button */}
                  <button
                    onClick={() =>
                      setShowDetails((prev) => ({
                        ...prev,
                        [alert.details?.alert_id]:
                          !prev[alert.details?.alert_id],
                      }))
                    }
                    className="mt-2 text-xs text-blue-600 hover:text-blue-800"
                  >
                    {showDetails[alert.details?.alert_id]
                      ? "Hide Details"
                      : "View Details"}
                  </button>

                  {/* Detailed View */}
                  {showDetails[alert.details?.alert_id] && (
                    <div className="mt-2 space-y-2">
                      {/* Trend Graphs */}
                      <div className="grid grid-cols-1 gap-2">
                        {renderTrendGraph(
                          alert.details?.temperature_history,
                          "Temperature"
                        )}
                        {renderTrendGraph(
                          alert.details?.oxygen_history,
                          "Oxygen"
                        )}
                        {renderTrendGraph(alert.details?.ph_history, "pH")}
                        {renderTrendGraph(
                          alert.details?.turbidity_history,
                          "Turbidity"
                        )}
                      </div>

                      {/* Recommendations */}
                      {alert.details?.recommendations && (
                        <div className="bg-gray-50 rounded p-2">
                          <h4 className="font-medium text-xs mb-1">
                            Recommendations:
                          </h4>
                          <ul className="list-disc pl-4 text-xs space-y-1">
                            {alert.details.recommendations.map((rec, i) => (
                              <li key={i}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-3 bg-gray-50 text-right">
            <button
              onClick={() => setIsOpen(false)}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
