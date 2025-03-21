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
import annotationPlugin from "chartjs-plugin-annotation";
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
  Legend,
  annotationPlugin
);

// Constants for parameter thresholds
const PARAMETER_THRESHOLDS = {
  temperature: {
    critical_low: 19,
    warning_low: 20,
    normal_low: 26,
    normal_high: 32,
    warning_high: 33,
    critical_high: 34,
    unit: "°C",
  },
  oxygen: {
    critical_low: 1.0,
    warning_low: 1.5,
    normal_low: 1.5,
    normal_high: 5.0,
    warning_high: 6.0,
    critical_high: 7.0,
    unit: "mg/L",
  },
  phlevel: {
    critical_low: 4.0,
    warning_low: 5.0,
    normal_low: 6.0,
    normal_high: 7.5,
    warning_high: 8.5,
    critical_high: 8.5,
    unit: "",
  },
  turbidity: {
    normal: 20,
    warning: 50,
    critical: 100,
    unit: "NTU",
  },
};

// Case styling definitions
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
    description: "Critical Temperature Level",
    borderLeft: "border-l-4 border-red-500",
    badge: "bg-red-600",
  },
  3: {
    bg: "bg-orange-100",
    border: "border-orange-500",
    text: "text-orange-700",
    label: "High",
    description: "Multiple Minor Water Fluctuation",
    borderLeft: "border-l-4 border-orange-500",
    badge: "bg-orange-500",
  },
  2: {
    bg: "bg-yellow-100",
    border: "border-yellow-500",
    text: "text-yellow-700",
    label: "Medium",
    description: "Minor Temperature Level",
    borderLeft: "border-l-4 border-yellow-500",
    badge: "bg-yellow-500",
  },
  1: {
    bg: "bg-green-100",
    border: "border-green-500",
    text: "text-green-700",
    label: "Normal",
    description: "Normal Temperature Level",
    borderLeft: "border-l-4 border-green-500",
    badge: "bg-green-500",
  },
};

// Priority level styling
const PRIORITY_STYLES = {
  Critical: "bg-red-100 border-red-500 text-red-700",
  High: "bg-orange-100 border-orange-500 text-orange-700",
  Medium: "bg-yellow-100 border-yellow-500 text-yellow-700",
  Normal: "bg-green-100 border-green-500 text-green-700",
};

const determineCaseLevel = (parameters) => {
  if (parameters.catfish_death === true) {
    return 5;
  }

  let minorFluctuations = 0;
  let hasMajorFluctuation = false;

  // Check all parameters for fluctuations
  Object.entries(parameters).forEach(([param, value]) => {
    if (["temperature", "oxygen", "phlevel"].includes(param.toLowerCase())) {
      const { hasFluctuation, isMajor } = checkParameterFluctuation(
        param,
        value
      );

      if (isMajor) {
        hasMajorFluctuation = true;
      } else if (hasFluctuation) {
        minorFluctuations++;
      }
    }
  });

  // Case determination based on rules
  if (hasMajorFluctuation) {
    return 4; // Any major fluctuation is automatically Case 4
  }
  if (minorFluctuations >= 2) {
    return 3; // Two or more minor fluctuations
  }
  if (minorFluctuations === 1) {
    return 2; // One minor fluctuation
  }
  return 1; // Normal conditions
};

// Utility Functions
const checkParameterFluctuation = (param, value) => {
  const thresholds = PARAMETER_THRESHOLDS[param.toLowerCase()];
  if (!thresholds) return { hasFluctuation: false, isMajor: false };

  switch (param.toLowerCase()) {
    case "oxygen":
      if (value < 1.0 || value > 7.0)
        return { hasFluctuation: true, isMajor: true }; // Major
      if (value >= 1.0 && value <= 1.4)
        return { hasFluctuation: true, isMajor: false }; // Minor
      if (value >= 5.0 && value <= 6.0)
        return { hasFluctuation: true, isMajor: false }; // Minor
      return { hasFluctuation: false, isMajor: false };

    case "phlevel":
      if (value < 5 || value >= 8.5)
        return { hasFluctuation: true, isMajor: true }; // Major
      if (value >= 5.0 && value <= 5.9)
        return { hasFluctuation: true, isMajor: false }; // Minor
      if (value >= 7.6 && value <= 8.5)
        return { hasFluctuation: true, isMajor: false }; // Minor
      return { hasFluctuation: false, isMajor: false };

    case "temperature":
      // Updated temperature ranges based on specifications
      if (value < 19 || value > 34)
        return { hasFluctuation: true, isMajor: true }; // Critical (Case 4)
      if (value >= 20 && value < 26)
        return { hasFluctuation: true, isMajor: false }; // Minor (Case 2)
      if (value >= 33 && value <= 34)
        return { hasFluctuation: true, isMajor: false }; // Minor (Case 2)
      if (value >= 26 && value <= 32)
        return { hasFluctuation: false, isMajor: false }; // Normal (Case 1)
      return { hasFluctuation: false, isMajor: false };

    default:
      return { hasFluctuation: false, isMajor: false };
  }
};

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
      return "text-orange-600 font-semibold";
    case "medium":
      return "text-yellow-600";
    case "normal":
      return "text-green-600";
    default:
      return "text-gray-600";
  }
};

const getStatusBackgroundColor = (status) => {
  switch (status.toLowerCase()) {
    case "critical":
      return "bg-red-50";
    case "warning":
      return "bg-orange-50";
    case "medium":
      return "bg-yellow-50";
    case "normal":
      return "bg-green-50";
    default:
      return "bg-gray-50";
  }
};

// Trend Graph rendering function
const renderTrendGraph = (data, parameter) => {
  if (!data || !data.datasets || !data.labels) {
    return null;
  }

  const thresholds = PARAMETER_THRESHOLDS[parameter.toLowerCase()];

  const options = {
    responsive: true,
    interaction: {
      mode: "index",
      intersect: false,
    },
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: `${parameter} Trend`,
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `${parameter}: ${context.parsed.y}${thresholds?.unit || ""}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: (context) => {
            if (!thresholds) return "rgba(0, 0, 0, 0.1)";
            const value = context.tick.value;
            if (parameter.toLowerCase() === "temperature") {
              if (value < 19 || value > 34) return "rgba(239, 68, 68, 0.2)"; // red
              if ((value >= 20 && value <= 25) || (value >= 33 && value <= 34))
                return "rgba(245, 158, 11, 0.2)"; // yellow
              if (value >= 26 && value <= 32) return "rgba(34, 197, 94, 0.2)"; // green
            }
            return "rgba(0, 0, 0, 0.1)";
          },
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          maxTicksLimit: 6,
        },
      },
    },
    elements: {
      line: {
        tension: 0.3,
      },
      point: {
        radius: 3,
      },
    },
  };

  return (
    <div className="bg-white p-2 rounded-lg shadow">
      <Line options={options} data={data} />
      <div className="mt-2 text-xs text-gray-500 text-center">
        Last updated: 2025-03-21 01:58:09
      </div>
    </div>
  );
};

export default function WaterQualityAlertBox({ alerts = [], removeAlert }) {
  const [showDetails, setShowDetails] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);
  const [incidentReport, setIncidentReport] = useState(null);
  const [previousCase, setPreviousCase] = useState(1);
  const dropdownRef = useRef(null);

  const CURRENT_TIMESTAMP = "2025-03-21 01:59:18";
  const CURRENT_USER = "LexusBelisario";

  const fetchIncidentReport = async () => {
    try {
      setIsLoading(true);
      console.log("Fetching incident report...");

      const response = await fetch(
        "http://localhost:5000/api/incident-report", // Updated URL
        {
          method: "GET",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Server error:", errorText);
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log("Received report data:", data);

      if (!data || !data.case) {
        console.warn("Invalid report format:", data);
        throw new Error("Invalid report format received");
      }

      const hasSignificantChange =
        data.case.number !== previousCase &&
        (data.case.number > previousCase || data.case.number > 1);

      if (hasSignificantChange) {
        setIncidentReport({
          ...data,
          timestamp: CURRENT_TIMESTAMP, // Updated timestamp
          reported_by: CURRENT_USER, // Updated user
        });
        setPreviousCase(data.case.number);

        const caseStyle = CASE_STYLES[data.case.number];
        if (data.case.number > 1) {
          toast.warn(
            `New Case ${data.case.number}: ${caseStyle.label} Alert - ${caseStyle.description}`,
            {
              position: "bottom-right",
              autoClose: 2000,
              hideProgressBar: false,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
              progress: undefined,
              className: caseStyle.bg,
              style: {
                borderLeft: `4px solid ${caseStyle.border.replace(
                  "border-",
                  ""
                )}`,
                color: caseStyle.text.replace("text-", ""),
              },
            }
          );
        }
      }
    } catch (error) {
      console.error("Fetch error details:", {
        message: error.message,
        stack: error.stack,
        type: error.name,
      });
      let errorMessage = "Failed to fetch incident report";
      if (
        error.name === "TypeError" &&
        error.message.includes("Failed to fetch")
      ) {
        errorMessage = "Network error: Please check your connection";
      } else if (error.message.includes("HTTP error!")) {
        errorMessage = `Server error: ${error.message}`;
      }

      toast.error(errorMessage, {
        position: "bottom-right",
        autoClose: 2000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const downloadPDF = async (incidentId) => {
    try {
      const response = await fetch(
        `http://localhost:5000/api/incident-report/${incidentId}/pdf`, // Updated URL
        {
          method: "GET",
          headers: {
            Accept: "application/pdf",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to download PDF");
      }

      const blob = await response.blob();
      if (blob.size === 0) {
        throw new Error("Received empty PDF file");
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      const caseNumber = incidentReport?.case?.number || 1;
      const caseStyle = CASE_STYLES[caseNumber];

      a.download = `water-quality-report-case${caseNumber}-${caseStyle.label.toLowerCase()}-${incidentId}-${CURRENT_TIMESTAMP.replace(
        /[: ]/g,
        "-"
      )}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success(
        `Case ${caseNumber} (${caseStyle.label}) report downloaded successfully`,
        {
          className: caseStyle.bg,
          style: {
            borderLeft: `4px solid ${caseStyle.border.replace("border-", "")}`,
            color: caseStyle.text.replace("text-", ""),
          },
        }
      );
    } catch (error) {
      console.error("Download error:", error);
      toast.error(`Failed to download report: ${error.message}`);
    }
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Fetch data effect
  useEffect(() => {
    let intervalId;

    const initFetch = async () => {
      await fetchIncidentReport();
      setIsLoading(false);
      intervalId = setInterval(fetchIncidentReport, 60000);
    };

    initFetch();

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [alerts]);

  // Calculate case counts
  const calculateCaseCounts = (alerts) => {
    return alerts.reduce((counts, alert) => {
      const caseLevel = determineCaseLevel(alert.details || {});
      counts[caseLevel] = (counts[caseLevel] || 0) + 1;
      return counts;
    }, {});
  };

  const caseCounts = calculateCaseCounts(alerts);
  const highestCaseLevel = Math.max(
    ...Object.keys(caseCounts).map(Number),
    incidentReport ? incidentReport.case.number : 1
  );

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
      {/* Bell Icon Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-[#E3D9C6] hover:text-[#8C7B6B] focus:outline-none"
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
        {Object.keys(caseCounts).length > 0 && (
          <span
            className={`absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 rounded-full ${CASE_STYLES[highestCaseLevel].badge}`}
          >
            {Object.values(caseCounts).reduce((sum, count) => sum + count, 0)}
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
                Water Quality Monitoring
              </h3>
              <div className="flex space-x-2">
                {Object.entries(caseCounts).map(([level, count]) => (
                  <span
                    key={level}
                    className={`px-2 py-1 text-xs font-semibold text-white rounded-full ${CASE_STYLES[level].badge}`}
                  >
                    {count} {CASE_STYLES[level].label}
                  </span>
                ))}
              </div>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Last updated: 2025-03-21 02:00:22
            </div>
          </div>

          {/* Alert List */}
          <div className="divide-y divide-gray-200">
            {alerts.length === 0 && !incidentReport && (
              <div className="px-4 py-3 text-sm text-gray-500">
                No active alerts
              </div>
            )}

            {alerts.map((alert, index) => {
              const caseLevel = determineCaseLevel(alert.details || {});
              const caseStyle = CASE_STYLES[caseLevel];

              return (
                <div
                  key={alert.details?.alert_id || index}
                  className={`px-4 py-3 hover:bg-gray-50 ${caseStyle.borderLeft}`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center space-x-2">
                        <p className={`text-sm font-medium ${caseStyle.text}`}>
                          Case {caseLevel}: {caseStyle.label}
                        </p>
                        <span
                          className={`px-2 py-0.5 text-xs font-semibold text-white rounded-full ${caseStyle.badge}`}
                        >
                          {caseStyle.description}
                        </span>
                      </div>
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
                    {Object.entries(alert.details || {})
                      .filter(([key]) =>
                        [
                          "temperature",
                          "oxygen",
                          "phlevel",
                          "turbidity",
                        ].includes(key)
                      )
                      .map(([key, value]) => {
                        const fluctuation = checkParameterFluctuation(
                          key,
                          value
                        );
                        const paramStyle = fluctuation.isMajor
                          ? CASE_STYLES[4]
                          : fluctuation.hasFluctuation
                          ? CASE_STYLES[2]
                          : CASE_STYLES[1];
                        return (
                          <div
                            key={key}
                            className={`p-1 rounded ${paramStyle.bg} border ${paramStyle.border}`}
                          >
                            <span className="font-medium">
                              {key.charAt(0).toUpperCase() + key.slice(1)}:
                            </span>{" "}
                            <span className={paramStyle.text}>
                              {typeof value === "number"
                                ? value.toFixed(2)
                                : value}
                              {PARAMETER_THRESHOLDS[key]?.unit}
                              {fluctuation.hasFluctuation && (
                                <span className="ml-1 text-xs">
                                  ({fluctuation.isMajor ? "Major" : "Minor"})
                                </span>
                              )}
                            </span>
                          </div>
                        );
                      })}
                  </div>

                  {/* Details Toggle */}
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

                  {/* Expanded Details */}
                  {showDetails[alert.details?.alert_id] && (
                    <div className="mt-2 space-y-2">
                      {/* Trend Graphs */}
                      <div className="grid grid-cols-1 gap-2">
                        {["Temperature", "Oxygen", "pH", "Turbidity"].map(
                          (param) =>
                            alert.details?.[
                              `${param.toLowerCase()}_history`
                            ] && (
                              <div key={param} className="mt-2">
                                {renderTrendGraph(
                                  alert.details[
                                    `${param.toLowerCase()}_history`
                                  ],
                                  param
                                )}
                              </div>
                            )
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Footer */}
          <div className="px-4 py-3 bg-gray-50 flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500">
                Generated by: LexusBelisario
              </span>
              {incidentReport && (
                <button
                  onClick={() => downloadPDF(incidentReport.incident_id)}
                  className="inline-flex items-center px-2 py-1 text-xs text-blue-600 hover:text-blue-800"
                >
                  <svg
                    className="w-4 h-4 mr-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  Download Report
                </button>
              )}
            </div>
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
