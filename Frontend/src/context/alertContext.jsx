import React, { useState } from "react";
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
  High: "bg-orange-100 border-orange-500 text-orange-700",
  Medium: "bg-yellow-100 border-yellow-500 text-yellow-700",
  Low: "bg-green-100 border-green-500 text-green-700",
  Normal: "bg-blue-100 border-blue-500 text-blue-700",
};

export default function WaterQualityAlertBox({ alerts, removeAlert }) {
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

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

  const getStatusColor = (status, value, parameter) => {
    const thresholds = PARAMETER_THRESHOLDS[parameter];
    if (value <= thresholds.critical_low || value >= thresholds.critical_high) {
      return "text-red-600 font-bold";
    }
    if (value <= thresholds.warning_low || value >= thresholds.warning_high) {
      return "text-orange-600";
    }
    return "text-green-600";
  };

  const renderTrendGraph = (data, parameter) => {
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
              const thresholds = PARAMETER_THRESHOLDS[parameter];
              const value = context.tick.value;
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
              return "rgba(0, 0, 0, 0.1)";
            },
          },
        },
      },
    };

    return <Line options={options} data={data} />;
  };

  const downloadReport = async (alertId) => {
    try {
      const response = await fetch(
        `http://localhost:5000/check_water_quality/print/${alertId}`,
        {
          method: "GET",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to download the report");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `water_quality_report_${alertId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading report:", error);
      alert("Failed to download the report. Please try again.");
    }
  };

  return (
    <div className="bg-white border border-gray-200 shadow-md rounded-lg p-4">
      <h2 className="text-lg font-bold text-blue-600 mb-4">
        Water Quality Monitoring
      </h2>

      {alerts.length === 0 ? (
        <p className="text-gray-500">
          All parameters are within normal ranges.
        </p>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert, index) => (
            <div
              key={index}
              className={`border rounded-lg p-4 ${
                PRIORITY_STYLES[alert.details.priority_level]
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-bold text-lg">
                    {alert.details.priority_level} Alert
                  </h3>
                  <p className="text-sm">{alert.details.time_detected}</p>
                </div>
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-white bg-opacity-50">
                  {alert.details.priority_level}
                </span>
              </div>

              {/* Current Readings */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <ParameterCard
                  name="Temperature"
                  value={alert.details.temperature}
                  unit="°C"
                  status={alert.details.temperature_status}
                  trend={alert.details.temperature_trend}
                />
                <ParameterCard
                  name="Oxygen"
                  value={alert.details.oxygen}
                  unit="mg/L"
                  status={alert.details.oxygen_status}
                  trend={alert.details.oxygen_trend}
                />
                <ParameterCard
                  name="pH Level"
                  value={alert.details.phlevel}
                  unit=""
                  status={alert.details.phlevel_status}
                  trend={alert.details.ph_trend}
                />
                <ParameterCard
                  name="Turbidity"
                  value={alert.details.turbidity}
                  unit="NTU"
                  status={alert.details.turbidity_status}
                  trend={alert.details.turbidity_trend}
                />
              </div>

              {/* Trend Graphs */}
              {showDetails && (
                <div className="mt-4 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {renderTrendGraph(
                      alert.details.temperature_history,
                      "temperature"
                    )}
                    {renderTrendGraph(alert.details.oxygen_history, "oxygen")}
                    {renderTrendGraph(alert.details.ph_history, "ph")}
                    {renderTrendGraph(
                      alert.details.turbidity_history,
                      "turbidity"
                    )}
                  </div>

                  {/* Predictions */}
                  <div className="bg-white bg-opacity-50 rounded-lg p-4">
                    <h4 className="font-semibold mb-2">
                      Predictions (Next 6 Hours)
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(alert.details.predictions).map(
                        ([param, values]) => (
                          <div key={param} className="space-y-2">
                            <p className="font-medium">{param}</p>
                            {values.map((value, i) => (
                              <p key={i} className="text-sm">
                                +{i + 1}h: {value.toFixed(2)}
                              </p>
                            ))}
                          </div>
                        )
                      )}
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="bg-white bg-opacity-50 rounded-lg p-4">
                    <h4 className="font-semibold mb-2">Recommended Actions</h4>
                    <ul className="list-disc pl-5 space-y-1">
                      {alert.details.recommendations
                        .split("\n")
                        .map((rec, i) => (
                          <li key={i} className="text-sm">
                            {rec}
                          </li>
                        ))}
                    </ul>
                  </div>
                </div>
              )}

              <div className="mt-4 flex justify-between items-center">
                <button
                  onClick={() => setShowDetails(!showDetails)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  {showDetails ? "Hide Details" : "Show Details"}
                </button>
                <button
                  onClick={() => downloadReport(alert.details.alert_id)}
                  className="group relative inline-flex h-10 items-center justify-center overflow-hidden rounded-md bg-blue-600 px-4 font-medium text-white hover:bg-blue-700"
                >
                  Download Report
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

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
    <div className={getStatusColor(status, value, name.toLowerCase())}>
      {status}
    </div>
  </div>
);
