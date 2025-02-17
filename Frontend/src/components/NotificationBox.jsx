import React, { useState, useEffect } from 'react';

const NotificationBox = () => {
    const [notifications, setNotifications] = useState([]);

    // Fetch notifications
    const fetchNotifications = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/notifications');
            const data = await response.json();
            setNotifications(data);
        } catch (error) {
            console.error('Error fetching notifications:', error);
        }
    };

    // Dismiss notification
    const dismissNotification = async (id) => {
        try {
            await fetch(`http://localhost:5000/api/dismiss/${id}`, {
                method: 'POST',
            });
            setNotifications(notifications.filter(n => n.id !== id));
        } catch (error) {
            console.error('Error dismissing notification:', error);
        }
    };

    // Check conditions periodically
    useEffect(() => {
        const checkConditions = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/water-conditions', {
                    method: 'POST',
                });
                const data = await response.json();
                if (data.alerts) {
                    fetchNotifications();
                }
            } catch (error) {
                console.error('Error checking conditions:', error);
            }
        };

        // Initial check
        checkConditions();

        // Set up interval
        const interval = setInterval(checkConditions, 60000); // Check every minute

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="fixed bottom-4 right-4 max-w-md">
            {notifications.map((notification) => (
                <div 
                    key={notification.id}
                    className="mb-4 bg-white rounded-lg shadow-lg p-4 border border-gray-200"
                >
                    <div className="flex justify-between items-start">
                        <div className="flex-1">
                            <p className="text-sm text-gray-500">
                                {notification.timestamp}
                            </p>
                            {notification.alerts.map((alert, index) => (
                                <div 
                                    key={index}
                                    className={`mt-2 p-2 rounded ${
                                        alert.status === 'critical' 
                                            ? 'bg-red-100 text-red-800' 
                                            : 'bg-yellow-100 text-yellow-800'
                                    }`}
                                >
                                    <p className="font-medium">
                                        {alert.type.toUpperCase()}: {alert.value}
                                    </p>
                                    <p className="text-sm">{alert.message}</p>
                                </div>
                            ))}
                        </div>
                        <button
                            onClick={() => dismissNotification(notification.id)}
                            className="ml-4 text-gray-400 hover:text-gray-500"
                        >
                            <span>×</span>
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default NotificationBox;