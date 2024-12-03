import React from "react";

export default function AlertBox({ alerts, removeAlert }) {
  const downloadReport = async (alertId) => {
    console.log("alertId:", alertId); // Debugging line
    try {
      const response = await fetch(
        `http://localhost:5000/check_dead_catfish/print/${alertId}`,
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
      a.download = `dead_catfish_report_${alertId}.pdf`; // Unique file for each alert
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
                        <strong>Possible Causes:</strong>
                        <ul className="list-disc pl-6">
                          {alert.details.possible_causes
                            .split("\n")
                            .map((cause, index) => (
                              <li key={index}>{cause}</li>
                            ))}
                        </ul>
                      </p>
                      <p>
                        <strong>Note:</strong> {alert.details.note}
                      </p>
                    </>
                  )}
                </div>
                <button
                  onClick={() => downloadReport(alert.details.alert_id)}
                  className="group relative inline-flex h-12 items-center justify-center overflow-hidden rounded-md bg-gradient-to-r from-[#D91656] to-[#640D5F] hover:from-[#640D5F] hover:to-[#D91656] px-6 font-medium text-neutral-200 duration-500 mt-2"
                >
                  <div className="translate-y-0 opacity-100 transition group-hover:-translate-y-[150%] group-hover:opacity-0">
                    Download Report
                  </div>
                  <div class="absolute translate-y-[150%] opacity-0 transition group-hover:translate-y-0 group-hover:opacity-100">
                    <svg
                      width="15"
                      height="15"
                      viewBox="0 0 15 15"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      class="h-6 w-6"
                    >
                      <path
                        d="M7.5 2C7.77614 2 8 2.22386 8 2.5L8 11.2929L11.1464 8.14645C11.3417 7.95118 11.6583 7.95118 11.8536 8.14645C12.0488 8.34171 12.0488 8.65829 11.8536 8.85355L7.85355 12.8536C7.75979 12.9473 7.63261 13 7.5 13C7.36739 13 7.24021 12.9473 7.14645 12.8536L3.14645 8.85355C2.95118 8.65829 2.95118 8.34171 3.14645 8.14645C3.34171 7.95118 3.65829 7.95118 3.85355 8.14645L7 11.2929L7 2.5C7 2.22386 7.22386 2 7.5 2Z"
                        fill="currentColor"
                        fill-rule="evenodd"
                        clip-rule="evenodd"
                      ></path>
                    </svg>
                  </div>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
