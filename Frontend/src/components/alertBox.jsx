// components/AlertBox.js
import React from "react";

export default function AlertBox({ alerts }) {
  return (
    <div className="bg-white border border-gray-200 shadow-md rounded-lg p-4">
      <h2 className="text-lg font-bold text-red-600 mb-2">
        Alert Notifications
      </h2>
      {alerts.length === 0 ? (
        <p className="text-gray-500">No alerts at this time.</p>
      ) : (
        <ul className="space-y-2">
          {alerts.map((alert, index) => (
            <li
              key={index}
              className={`p-2 rounded-md ${
                alert.includes("died")
                  ? "bg-red-100 text-red-800"
                  : "bg-yellow-100 text-yellow-800"
              }`}
            >
              {alert}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
