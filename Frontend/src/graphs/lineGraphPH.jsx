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
        setPhData(processPhData(data));
        setLoading(false);
      } catch (error) {
        console.error("Error fetching pH data:", error);
        setLoading(false);
      }
    };
    fetchPhData();
  }, [filter]); // refetch data when filter changes

  const processPhData = (data) => {
    const labels = [];
    const phLevels = [];

    if (filter === "3hours") {
      data.forEach((entry) => {
        const date = new Date(entry.timeData);
        labels.push(`${date.getHours()}:00 ${date.toLocaleDateString()}`);
        phLevels.push(entry.phlevel);
      });
    } else {
      const dailyPhLevels = Array(7)
        .fill(0)
        .map(() => []);

      data.forEach((entry) => {
        const date = new Date(entry.timeData);
        const phLevel = entry.phlevel;
        const dayIndex = date.getDay();
        dailyPhLevels[dayIndex].push(phLevel);
      });

      const avgPhLevels = dailyPhLevels.map((phArray) => {
        if (phArray.length === 0) return 0;
        return phArray.reduce((sum, ph) => sum + ph, 0) / phArray.length;
      });

      labels.push(
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
      );
      phLevels.push(...avgPhLevels);
    }

    return {
      labels,
      datasets: [
        {
          label: filter === "3hours" ? "pH Levels (3-hour intervals)" : "Weekly pH Levels",
          data: phLevels,
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
        text: filter === "3hours" ? "pH Levels Every 3 Hours" : "Weekly pH Levels",
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
