import React, { useState, useEffect } from "react";

const NotificationBox = () => {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/notifications");
      const data = await response.json();
      setNotifications(data.filter((n) => !n.dismissed));
    } catch (error) {
      console.error("Error fetching notifications:", error);
    }
  };

  const dismissNotification = async (id) => {
    try {
      await fetch(`http://localhost:5000/api/dismiss-notification/${id}`, {
        method: "POST",
      });
      setNotifications(notifications.filter((n) => n.id !== id));
    } catch (error) {
      console.error("Error dismissing notification:", error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "Critical":
        return "bg-red-100 text-red-800";
      case "Below Average":
        return "bg-yellow-100 text-yellow-800";
      case "Above Average":
        return "bg-orange-100 text-orange-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="fixed bottom-4 right-4 max-w-sm w-full">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className="mb-4 bg-white rounded-lg shadow-lg p-4 border border-gray-200"
        >
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <p className="text-sm text-gray-500">{notification.timestamp}</p>
              {notification.conditions.map((condition, index) => (
                <div
                  key={index}
                  className={`mt-2 p-2 rounded-md ${getStatusColor(
                    condition.status
                  )}`}
                >
                  <p className="font-medium">
                    {condition.parameter}: {condition.value}
                  </p>
                  <p className="text-sm">{condition.message}</p>
                </div>
              ))}
            </div>
            <button
              onClick={() => dismissNotification(notification.id)}
              className="ml-4 text-gray-400 hover:text-gray-500"
            >
              <span className="sr-only">Dismiss</span>
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default NotificationBox;
