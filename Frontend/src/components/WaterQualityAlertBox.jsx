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
    critical_low: 19,
    warning_low: 20,
    normal_low: 26,
    normal_high: 32,
    warning_high: 33,
    critical_high: 33,
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
  ph: {
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

// Priority level styling
const PRIORITY_STYLES = {
  Critical: "bg-red-100 border-red-500 text-red-700",
  High: "bg-orange-100 border-orange-500 text-orange-700",
  Medium: "bg-yellow-100 border-yellow-500 text-yellow-700",
  Normal: "bg-green-100 border-green-500 text-green-700",
};

// Case styling
const CASE_STYLES = {
  4: {
    bg: "bg-red-100",
    border: "border-red-500",
    text: "text-red-700",
    label: "Critical",
  },
  3: {
    bg: "bg-orange-100",
    border: "border-orange-500",
    text: "text-orange-700",
    label: "High",
  },
  2: {
    bg: "bg-yellow-100",
    border: "border-yellow-500",
    text: "text-yellow-700",
    label: "Medium",
  },
  1: {
    bg: "bg-green-100",
    border: "border-green-500",
    text: "text-green-700",
    label: "Normal",
  },
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
    case "high":
      return "text-orange-600";
    case "medium":
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

// Incident Details Component
const IncidentDetails = ({ incident, onDownload }) => (
  <div
    className={`p-4 rounded-lg mb-4 ${CASE_STYLES[incident.case.number].bg} ${
      CASE_STYLES[incident.case.number].border
    } border`}
  >
    <div className="flex justify-between items-start">
      <div>
        <h3 className={`font-bold ${CASE_STYLES[incident.case.number].text}`}>
          {incident.case.title}
        </h3>
        <p className="text-sm mt-1">{incident.case.description}</p>
        <p className="text-xs text-gray-500 mt-1">
          Detected at: 2025-03-20 14:30:22
        </p>
      </div>

      {/* Download Button */}
      <button
        onClick={() => onDownload(incident.incident_id)}
        className="inline-flex items-center px-3 py-1 border border-blue-500 shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-blue-500 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
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
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        Download Report
      </button>
    </div>

    {/* Current Readings */}
    <div className="mt-4 grid grid-cols-3 gap-4">
      {Object.entries(incident.current_readings).map(([param, data]) => (
        <ParameterCard
          key={param}
          name={param.charAt(0).toUpperCase() + param.slice(1)}
          value={data.value.toFixed(2)}
          unit={PARAMETER_THRESHOLDS[param.toLowerCase()]?.unit || ""}
          status={data.status}
        />
      ))}
    </div>

    {/* Recommendations */}
    {incident.recommendations && incident.recommendations.length > 0 && (
      <div className="mt-4">
        <h4 className="font-semibold mb-2">Recommendations:</h4>
        <ul className="space-y-2">
          {incident.recommendations.map((rec, index) => (
            <li
              key={index}
              className={`p-2 rounded ${PRIORITY_STYLES[rec.priority]}`}
            >
              <span className="font-medium">{rec.action}</span>
              <ul className="mt-1 ml-4 list-disc">
                {rec.details.map((detail, i) => (
                  <li key={i} className="text-sm">
                    {detail}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </div>
    )}

    <div className="mt-4 text-xs text-gray-500">
      Report ID: {incident.incident_id}
      <br />
      Generated by: LexusBelisario
      <br />
      Last updated: 2025-03-20 14:30:22
    </div>
  </div>
);

export default function WaterQualityAlertBox({ alerts = [], removeAlert }) {
  const [showDetails, setShowDetails] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);
  const [incidentReport, setIncidentReport] = useState(null);
  const [previousCase, setPreviousCase] = useState(1);
  const dropdownRef = useRef(null);

  const CURRENT_TIMESTAMP = "2025-03-20 14:31:26";
  const CURRENT_USER = "LexusBelisario";

  // Fetch incident reports
  const fetchIncidentReport = async () => {
    try {
      const response = await fetch("/api/incident-report");
      const data = await response.json();

      // Only update if case number changes and it's not returning to normal from a higher case
      if (
        data.case.number !== previousCase &&
        !(previousCase > 1 && data.case.number === 1)
      ) {
        setIncidentReport({
          ...data,
          timestamp: CURRENT_TIMESTAMP,
          reported_by: CURRENT_USER,
        });
        setPreviousCase(data.case.number);

        // Show toast notification for new incident
        toast.warn(`New ${data.case.title}`, {
          position: "top-right",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });
      }
    } catch (error) {
      console.error("Error fetching incident report:", error);
      toast.error("Failed to fetch incident report");
    }
  };

  // Download PDF report
  const downloadPDF = async (incidentId) => {
    try {
      const response = await fetch(`/api/incident-report/${incidentId}/pdf`);
      if (!response.ok) {
        throw new Error("Failed to download PDF");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      // Add case information to the filename
      const caseLevel =
        incidentReport?.case?.number === 1
          ? "normal"
          : incidentReport?.case?.number === 2
          ? "medium"
          : incidentReport?.case?.number === 3
          ? "high"
          : "critical";

      a.download = `water-quality-report-${caseLevel}-${incidentId}-2025-03-20-14-34-16.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success(
        `${
          caseLevel.charAt(0).toUpperCase() + caseLevel.slice(1)
        } report downloaded successfully`
      );
    } catch (error) {
      console.error("Error downloading PDF:", error);
      toast.error("Failed to download PDF report");
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

  useEffect(() => {
    // Initial fetch
    fetchIncidentReport();

    // Set up interval for periodic checks
    const interval = setInterval(fetchIncidentReport, 60000); // Check every minute

    console.log("Water Quality Alerts:", alerts);
    setIsLoading(false);

    return () => clearInterval(interval);
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
                if (
                  value === thresholds.critical_low ||
                  value === thresholds.critical_high
                ) {
                  return "rgba(255, 0, 0, 0.2)";
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

        {(criticalCount + warningCount > 0 || incidentReport) && ( // Removed the case.number > 1 check
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 rounded-full bg-red-600">
            {criticalCount + warningCount + (incidentReport ? 1 : 0)}
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
            <div className="text-xs text-gray-500 mt-1">
              Last updated: 2025-03-20 14:32:13
            </div>
          </div>

          {/* Current Incident Report (if any) */}
          {incidentReport && ( // Removed the case.number > 1 check
            <IncidentDetails
              incident={incidentReport}
              onDownload={downloadPDF}
            />
          )}

          {/* Alert List */}
          <div className="divide-y divide-gray-200">
            {alerts.length === 0 && !incidentReport && (
              <div className="px-4 py-3 text-sm text-gray-500">
                No readings available
              </div>
            )}

            {alerts.map((alert, index) => (
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
                      {new Date(alert.details?.time_detected).toLocaleString()}
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
                    .map(([key, value]) => (
                      <div key={key}>
                        <span className="font-medium">
                          {key.charAt(0).toUpperCase() + key.slice(1)}:
                        </span>{" "}
                        {value} {PARAMETER_THRESHOLDS[key]?.unit}
                      </div>
                    ))}
                </div>

                <button
                  onClick={() =>
                    setShowDetails((prev) => ({
                      ...prev,
                      [alert.details?.alert_id]: !prev[alert.details?.alert_id],
                    }))
                  }
                  className="mt-2 text-xs text-blue-600 hover:text-blue-800"
                >
                  {showDetails[alert.details?.alert_id]
                    ? "Hide Details"
                    : "View Details"}
                </button>

                {showDetails[alert.details?.alert_id] && (
                  <div className="mt-2 space-y-2">
                    <div className="grid grid-cols-1 gap-2">
                      {["Temperature", "Oxygen", "pH", "Turbidity"].map(
                        (param) =>
                          alert.details?.[`${param.toLowerCase()}_history`] && (
                            <div key={param} className="mt-2">
                              {renderTrendGraph(
                                alert.details[`${param.toLowerCase()}_history`],
                                param
                              )}
                            </div>
                          )
                      )}
                    </div>

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
            ))}
          </div>

          {/* Footer */}
          <div className="px-4 py-3 bg-gray-50 flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500">
                Generated by: LexusBelisario
              </span>
              {incidentReport && ( // Removed the case.number > 1 check
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
                  Download {incidentReport.case.number === 1 ? "Normal " : ""}
                  Report
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
