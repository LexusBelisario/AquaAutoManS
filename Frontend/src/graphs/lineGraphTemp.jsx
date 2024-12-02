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
  const [filter, setFilter] = useState("weekly"); // default filter is 'weekly'
  const [selectedDate, setSelectedDate] = useState(""); // state to store selected date
  const [weekStart, setWeekStart] = useState(""); // state to store selected week start date

  useEffect(() => {
    const fetchTemperatureData = async () => {
      try {
        let url = `http://127.0.0.1:5000/filtered-temperature-data?filter=${filter}`;

        // Append the selected date or week start to the request if available
        if (filter === "date" && selectedDate) {
          url += `&selected_date=${selectedDate}`;
        } else if (filter === "week" && weekStart) {
          url += `&week_start=${weekStart}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        console.log("Fetched data:", data);

        const processedData = processTemperatureData(data);
        setTemperatureData(processedData);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching temperature data:", error);
        setLoading(false);
      }
    };
    fetchTemperatureData();
  }, [filter, selectedDate, weekStart]); // refetch data when filter, selectedDate, or weekStart changes

  const processTemperatureData = (data) => {
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
    const temperatures =
      filter === "3hours" ? [] : [50, 40, 30, 20, 10, 0].map(() => []);

    const dailyTemperatures = Array(7)
      .fill(0)
      .map(() => []);

    data.forEach((entry) => {
      const date = new Date(entry.timeData);
      const temp = entry.temperature;

      if (filter === "3hours") {
        const timeLabel = `${date.getHours()}:00 ${date.toLocaleDateString()}`;
        labels.push(timeLabel);
        temperatures.push(temp);
      } else {
        const dayIndex = date.getDay();
        if (dayIndex >= 1) {
          dailyTemperatures[dayIndex - 1].push(temp);
        }
      }
    });

    const avgTemperatures = dailyTemperatures.map((tempArray) => {
      if (tempArray.length === 0) return 0;
      return tempArray.reduce((sum, temp) => sum + temp, 0) / tempArray.length;
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
              ? "Temperature Every 3 Hours"
              : "Average Temperature",
          data: filter === "3hours" ? temperatures : avgTemperatures,
          fill: false,
          borderColor: "#FF5F1F",
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
            ? "Temperature Every 3 Hours"
            : "Weekly Temperature",
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

      {/* Show input fields based on selected filter */}
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

      {temperatureData.labels.length > 0 ? (
        <Line options={options} data={temperatureData} />
      ) : (
        <div>No data available to display</div>
      )}
    </div>
  );
};
