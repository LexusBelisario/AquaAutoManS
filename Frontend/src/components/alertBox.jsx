import React from "react";

export default function AlertBox({ alerts, removeAlert }) {
  const downloadReport = async () => {
    try {
      const response = await fetch(
        "http://localhost:5000/check_dead_catfish/print",
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
      a.download = "dead_catfish_report.pdf";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading report:", error);
      alert("Failed to download the report. Please try again.");
    }
  };
  return (
    <div className="bg-white border border-gray-200 shadow-md rounded-lg p-4">
      <h2 className="text-lg font-bold text-red-600 mb-2">
        Alert Notifications
      </h2>
      {alerts.length === 0 ? (
        <p className="text-gray-500">No alerts at this time.</p>
      ) : (
        <ul className="space-y-2">
          {alerts.map((alert, index) => {
            // Check if the alert is about "No dead catfish detected"
            const isNoDeadCatfish =
              alert.details.message ===
              "No dead catfish detected in the system.";

            return (
              <li
                key={index}
                className={`p-2 rounded-md ${
                  isNoDeadCatfish
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
                } flex flex-col justify-between items-start`}
              >
                <span className="font-bold">{alert.alert}</span>
                <div className="text-sm mt-1">
                  {isNoDeadCatfish ? (
                    <p className="text-green-800">{alert.details.message}</p>
                  ) : (
                    <>
                      <p>
                        <strong>Time Detected:</strong>{" "}
                        {alert.details.time_detected}
                      </p>
                      <p>
                        <strong>Dead Catfish Count:</strong>{" "}
                        {alert.details.dead_catfish_count}
                      </p>
                      <p>
                        <strong>Temperature:</strong>{" "}
                        {alert.details.temperature}°C (
                        {alert.details.temperature_status})
                      </p>
                      <p>
                        <strong>Oxygen:</strong> {alert.details.oxygen} mg/L (
                        {alert.details.oxygen_status})
                      </p>
                      <p>
                        <strong>pH Level:</strong> {alert.details.phlevel} (
                        {alert.details.phlevel_status})
                      </p>
                      <p>
                        <strong>Turbidity:</strong> {alert.details.turbidity}{" "}
                        NTU ({alert.details.turbidity_status})
                      </p>
                      <p>
                        <strong>Possible Causes:</strong>{" "}
                        {alert.details.possible_causes}
                      </p>
                      <p>
                        <strong>Note:</strong> {alert.details.note}
                      </p>
                    </>
                  )}
                </div>
                <button
                  onClick={downloadReport}
                  className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-md shadow hover:bg-blue-600"
                >
                  Download Report
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
