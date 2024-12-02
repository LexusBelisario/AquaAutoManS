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

export const LineGraphTurb = () => {
  const [turbidityData, setTurbidityData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("weekly");
  const [selectedDate, setSelectedDate] = useState("");
  const [weekStart, setWeekStart] = useState("");

  useEffect(() => {
    const fetchTurbidityData = async () => {
      try {
        let url = `http://127.0.0.1:5000/filtered-turbidity-data?filter=${filter}`;

        if (filter === "date" && selectedDate) {
          url += `&selected_date=${selectedDate}`;
        } else if (filter === "week" && weekStart) {
          url += `&week_start=${weekStart}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        console.log("Fetched turbidity data:", data);

        const processedData = processTurbidityData(data);
        setTurbidityData(processedData);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching turbidity data:", error);
        setLoading(false);
      }
    };
    fetchTurbidityData();
  }, [filter, selectedDate, weekStart]);

  const processTurbidityData = (data) => {
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
    const turbidityLevels =
      filter === "3hours" ? [] : [100, 80, 60, 40, 20, 0].map(() => []);

    const dailyTurbidityLevels = Array(7)
      .fill(0)
      .map(() => []);

    data.forEach((entry) => {
      const date = new Date(entry.timeData);
      const turbidity = entry.turbidity;

      if (filter === "3hours") {
        const timeLabel = `${date.getHours()}:00 ${date.toLocaleDateString()}`;
        labels.push(timeLabel);
        turbidityLevels.push(turbidity);
      } else {
        const dayIndex = date.getDay();
        if (dayIndex >= 1) {
          dailyTurbidityLevels[dayIndex - 1].push(turbidity);
        }
      }
    });

    const avgTurbidityLevels = dailyTurbidityLevels.map((turbidityArray) => {
      if (turbidityArray.length === 0) return 0;
      return (
        turbidityArray.reduce((sum, turb) => sum + turb, 0) /
        turbidityArray.length
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
              ? "Turbidity Every 3 Hours"
              : "Average Turbidity",
          data: filter === "3hours" ? turbidityLevels : avgTurbidityLevels,
          fill: false,
          borderColor: "#FFEB3B",
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
          filter === "3hours" ? "Turbidity Every 3 Hours" : "Weekly Turbidity",
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
          <option value="date">By Date</option>
          <option value="week">By Week</option>
        </select>
      </div>

      {filter === "date" && (
        <div className="mb-4">
          <label>Select Date: </label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
        </div>
      )}

      {filter === "week" && (
        <div className="mb-4">
          <label>Select Week Start (Sunday): </label>
          <input
            type="date"
            value={weekStart}
            onChange={(e) => setWeekStart(e.target.value)}
          />
        </div>
      )}

      {turbidityData.labels.length > 0 ? (
        <Line options={options} data={turbidityData} />
      ) : (
        <div>No data available to display</div>
      )}
    </div>
  );
};
