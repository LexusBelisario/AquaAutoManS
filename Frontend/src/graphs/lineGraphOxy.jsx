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

export const LineGraphOxygen = () => {
  const [oxygenData, setOxygenData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("weekly"); // default filter is 'weekly'

  useEffect(() => {
    const fetchOxygenData = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/weekly-oxygen-data?filter=${filter}`
        );
        const data = await response.json();

        console.log("Fetched data:", data);

        const processedData = processOxygenData(data);

        setOxygenData(processedData);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching oxygen data:", error);
        setLoading(false);
      }
    };
    fetchOxygenData();
  }, [filter]); // refetch data when filter changes

  const processOxygenData = (data) => {
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
    const oxygenLevels =
      filter === "3hours" ? [] : [50, 40, 30, 20, 10, 0].map(() => []);

    const dailyOxygenLevels = Array(7)
      .fill(0)
      .map(() => []);

    data.forEach((entry) => {
      const date = new Date(entry.timeData);
      const oxygenLevel = entry.oxygen_level;

      if (filter === "3hours") {
        const timeLabel = `${date.getHours()}:00 ${date.toLocaleDateString()}`;
        labels.push(timeLabel);
        oxygenLevels.push(oxygenLevel);
      } else {
        const dayIndex = date.getDay();
        if (dayIndex >= 1) {
          dailyOxygenLevels[dayIndex - 1].push(oxygenLevel);
        }
      }
    });

    const avgOxygenLevels = dailyOxygenLevels.map((oxygenArray) => {
      if (oxygenArray.length === 0) return 0;
      return (
        oxygenArray.reduce((sum, oxygenLevel) => sum + oxygenLevel, 0) /
        oxygenArray.length
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
              ? "Oxygen Levels Every 3 Hours"
              : "Average Oxygen Levels",
          data: filter === "3hours" ? oxygenLevels : avgOxygenLevels,
          fill: false,
          borderColor: "green",
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
          filter === "3hours"
            ? "Oxygen Levels Every 3 Hours"
            : "Weekly Oxygen Levels",
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
      {oxygenData.labels.length > 0 ? (
        <Line options={options} data={oxygenData} />
      ) : (
        <div>No data available to display</div>
      )}
    </div>
  );
};
