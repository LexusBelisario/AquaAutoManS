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

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export const LineGraphTemp = () => {
  const [temperatureData, setTemperatureData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTemperatureData = async () => {
      try {
        const response = await fetch(
          "http://localhost:5000/weekly-temperature-data"
        );
        const data = await response.json();

        console.log("Fetched data:", data); // Debugging: Check the fetched data

        // Process data to group by day of the week
        const processedData = processTemperatureData(data);

        setTemperatureData(processedData);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching temperature data:", error);
        setLoading(false);
      }
    };

    fetchTemperatureData();
  }, []);

  // Process data to fit temperature intervals and days of the week
  const processTemperatureData = (data) => {
    const labels = [
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
      "Sunday",
    ];
    const temperatures = [50, 40, 30, 20, 10, 0].map(() => []);

    // Initialize temperature data arrays for each day of the week
    const dailyTemperatures = Array(7)
      .fill(0)
      .map(() => []);

    data.forEach((entry) => {
      const date = new Date(entry.timeData);
      const dayIndex = date.getDay(); // 0 = Sunday, 1 = Monday, ..., 6 = Saturday
      const temp = entry.temperature;

      if (dayIndex >= 1) {
        // Convert Sunday to last index of the week
        dailyTemperatures[dayIndex - 1].push(temp);
      }
    });

    // Convert daily temperature arrays to average temperatures
    const avgTemperatures = dailyTemperatures.map((tempArray) => {
      if (tempArray.length === 0) return 0;
      return tempArray.reduce((sum, temp) => sum + temp, 0) / tempArray.length;
    });

    return {
      labels: labels,
      datasets: [
        {
          label: "Average Temperature",
          data: avgTemperatures,
          fill: false,
          borderColor: "blue",
          tension: 0.1,
        },
      ],
    };
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: "Weekly Temperature",
      },
    },
  };

  return loading ? (
    <div>Loading...</div>
  ) : (
    <div className="w-full max-w-screen-lg mx-auto">
      {temperatureData.labels.length > 0 ? (
        <Line options={options} data={temperatureData} />
      ) : (
        <div>No data available to display</div>
      )}
    </div>
  );
};
