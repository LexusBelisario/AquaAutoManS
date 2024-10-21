import React from "react";

const AlertBox = ({ alerts }) => {
  return (
    <div className="bg-red-100 border border-red-400 text-red-700 p-4 rounded relative">
      {alerts.length === 0 ? (
        <p>No alerts</p>
      ) : (
        alerts.map((alert, index) => <p key={index}>{alert}</p>)
      )}
    </div>
  );
};

export default AlertBox;
