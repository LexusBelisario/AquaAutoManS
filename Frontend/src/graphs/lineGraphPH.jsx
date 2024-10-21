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

export const LineGraphPH = () => {
  const [phData, setPhData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("weekly"); // default filter is 'weekly'

  useEffect(() => {
    const fetchPhData = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/weekly-ph-data?filter=${filter}`
        );
        const data = await response.json();

        console.log("Fetched data:", data);

        const processedData = processPhData(data);

        setPhData(processedData);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching pH data:", error);
        setLoading(false);
      }
    };
    fetchPhData();
  }, [filter]); // refetch data when filter changes

  const processPhData = (data) => {
    const labels =
      filter === "3hours"
        ? []
        : [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
          ];
    const phLevels =
      filter === "3hours" ? [] : [50, 40, 30, 20, 10, 0].map(() => []);

    const dailyPhLevels = Array(7)
      .fill(0)
      .map(() => []);

    data.forEach((entry) => {
      const date = new Date(entry.timeData);
      const phLevel = entry.ph_level;

      if (filter === "3hours") {
        const timeLabel = `${date.getHours()}:00 ${date.toLocaleDateString()}`;
        labels.push(timeLabel);
        phLevels.push(phLevel);
      } else {
        const dayIndex = date.getDay();
        if (dayIndex >= 1) {
          dailyPhLevels[dayIndex - 1].push(phLevel);
        }
      }
    });

    const avgPhLevels = dailyPhLevels.map((phArray) => {
      if (phArray.length === 0) return 0;
      return (
        phArray.reduce((sum, phLevel) => sum + phLevel, 0) / phArray.length
      );
    });

    return {
      labels:
        filter === "3hours"
          ? labels
          : [
              "Monday",
              "Tuesday",
              "Wednesday",
              "Thursday",
              "Friday",
              "Saturday",
              "Sunday",
            ],
      datasets: [
        {
          label:
            filter === "3hours"
              ? "pH Levels Every 3 Hours"
              : "Average pH Levels",
          data: filter === "3hours" ? phLevels : avgPhLevels,
          fill: false,
          borderColor: "purple",
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
        text:
          filter === "3hours" ? "pH Levels Every 3 Hours" : "Weekly pH Levels",
      },
    },
  };

  return loading ? (
    <div>Loading...</div>
  ) : (
    <div className="w-full max-w-screen-lg mx-auto">
      <div className="mb-4">
        <label>Filter: </label>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="weekly">Weekly</option>
          <option value="3hours">Every 3 Hours</option>
        </select>
      </div>
      {phData.labels.length > 0 ? (
        <Line options={options} data={phData} />
      ) : (
        <div>No data available to display</div>
      )}
    </div>
  );
};
