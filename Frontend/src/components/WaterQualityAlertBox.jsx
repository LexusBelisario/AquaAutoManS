import React, { useEffect, useState } from "react";
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
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

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

export default function WaterQualityAlertBox({ alerts = [], removeAlert }) {
  const [showDetails, setShowDetails] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    console.log('Water Quality Alerts:', alerts);
    setIsLoading(false);
  }, [alerts]);

  const toggleDetails = (alertId) => {
    setShowDetails(prev => ({
      ...prev,
      [alertId]: !prev[alertId]
    }));
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
    switch (status.toLowerCase()) {
      case 'critical':
        return "text-red-600 font-bold";
      case 'warning':
        return "text-yellow-600";
      case 'normal':
        return "text-green-600";
      default:
        return "text-gray-600";
    }
  };

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
                if (value === thresholds.normal_low || value === thresholds.normal_high) {
                  return "rgba(0, 255, 0, 0.2)";
                }
                if (value === thresholds.warning_low || value === thresholds.warning_high) {
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

  const notifyWaterQualityIssue = (alert) => {
    const priority = alert.details.priority_level;
    const toastOptions = {
      position: "top-right",
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
    };

    switch (priority) {
      case 'Critical':
        toast.error(`Critical Alert: ${alert.details.detected_issues.join(', ')}`, toastOptions);
        break;
      case 'Warning':
        toast.warning(`Warning: ${alert.details.detected_issues.join(', ')}`, toastOptions);
        break;
      default:
        toast.info(`Water quality update`, toastOptions);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white border border-gray-200 shadow-md rounded-lg p-4">
        <p className="text-gray-500">Loading water quality data...</p>
      </div>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <div className="bg-white border border-gray-200 shadow-md rounded-lg p-4">
        <p className="text-gray-500">No active water quality alerts</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 shadow-md rounded-lg p-4">
      <h2 className="text-lg font-bold text-blue-600 mb-4">
        Water Quality Alerts ({alerts.length})
      </h2>
      <div className="space-y-4">
        {alerts.map((alert, index) => (
          <div
            key={alert.details?.alert_id || index}
            className={`border rounded-lg p-4 ${
              PRIORITY_STYLES[alert.details?.priority_level || 'Normal']
            }`}
          >
            {/* Alert Header */}
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="font-bold text-lg">
                  {alert.details?.priority_level || 'Normal'} Alert
                </h3>
                <p className="text-sm">{alert.details?.time_detected}</p>
              </div>
              <div className="flex items-center space-x-2">
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-white bg-opacity-50">
                  {alert.details?.priority_level || 'Normal'}
                </span>
                <button
                  onClick={() => removeAlert(alert.details?.alert_id)}
                  className="text-gray-500 hover:text-red-500"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Parameter Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <ParameterCard
                name="Temperature"
                value={alert.details?.temperature}
                unit="°C"
                status={alert.details?.temperature_status}
                trend={alert.details?.temperature_trend}
              />
              <ParameterCard
                name="Oxygen"
                value={alert.details?.oxygen}
                unit="mg/L"
                status={alert.details?.oxygen_status}
                trend={alert.details?.oxygen_trend}
              />
              <ParameterCard
                name="pH Level"
                value={alert.details?.phlevel}
                unit=""
                status={alert.details?.phlevel_status}
                trend={alert.details?.ph_trend}
              />
              <ParameterCard
                name="Turbidity"
                value={alert.details?.turbidity}
                unit="NTU"
                status={alert.details?.turbidity_status}
                trend={alert.details?.turbidity_trend}
              />
            </div>

            {/* Issues and Recommendations */}
            {alert.details?.detected_issues && alert.details.detected_issues.length > 0 && (
              <div className="mt-4 space-y-2">
                <h4 className="font-semibold">Detected Issues:</h4>
                <ul className="list-disc pl-5">
                  {alert.details.detected_issues.map((issue, i) => (
                    <li key={i} className="text-sm text-red-600">{issue}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Toggle Details Button */}
            <button
              onClick={() => toggleDetails(alert.details?.alert_id)}
              className="mt-4 text-blue-600 hover:text-blue-800"
            >
              {showDetails[alert.details?.alert_id] ? 'Hide Details' : 'Show Details'}
            </button>

            {/* Detailed View */}
            {showDetails[alert.details?.alert_id] && (
              <div className="mt-4 space-y-4">
                {/* Trend Graphs */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {renderTrendGraph(alert.details?.temperature_history, "Temperature")}
                  {renderTrendGraph(alert.details?.oxygen_history, "Oxygen")}
                  {renderTrendGraph(alert.details?.ph_history, "pH")}
                  {renderTrendGraph(alert.details?.turbidity_history, "Turbidity")}
                </div>

                {/* Predictions */}
                {alert.details?.predictions && (
                  <div className="bg-white bg-opacity-50 rounded-lg p-4">
                    <h4 className="font-semibold mb-2">Predictions (Next 6 Hours)</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(alert.details.predictions).map(([param, values]) => (
                        <div key={param} className="space-y-2">
                          <p className="font-medium">{param}</p>
                          {values.map((value, i) => (
                            <p key={i} className="text-sm">
                              +{i + 1}h: {value.toFixed(2)}
                            </p>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                {alert.details?.recommendations && (
                  <div className="bg-white bg-opacity-50 rounded-lg p-4">
                    <h4 className="font-semibold mb-2">Recommended Actions</h4>
                    <ul className="list-disc pl-5 space-y-1">
                      {alert.details.recommendations.map((rec, i) => (
                        <li key={i} className="text-sm">{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
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
    <div className={getStatusColor(status)}>
      {status}
    </div>
  </div>
);