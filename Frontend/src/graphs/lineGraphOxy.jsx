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
  const [selectedDate, setSelectedDate] = useState(""); // state to store selected date
  const [weekStart, setWeekStart] = useState(""); // state to store selected week start date

  useEffect(() => {
    const fetchOxygenData = async () => {
      try {
        let url = `http://127.0.0.1:5000/filtered-oxygen-data?filter=${filter}`;

        // Append the selected date or week start to the request if available
        if (filter === "date" && selectedDate) {
          url += `&selected_date=${selectedDate}`;
        } else if (filter === "week" && weekStart) {
          url += `&week_start=${weekStart}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        console.log("Fetched oxygen data:", data);

        const processedData = processOxygenData(data);
        setOxygenData(processedData);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching oxygen data:", error);
        setLoading(false);
      }
    };
    fetchOxygenData();
  }, [filter, selectedDate, weekStart]); // refetch data when filter, selectedDate, or weekStart changes

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
      filter === "3hours" ? [] : [5, 4, 3, 2, 1, 0].map(() => []);

    const dailyOxygenLevels = Array(7)
      .fill(0)
      .map(() => []);

    data.forEach((entry) => {
      const date = new Date(entry.timeData);
      const oxygen = entry.oxygen;

      if (filter === "3hours") {
        const timeLabel = `${date.getHours()}:00 ${date.toLocaleDateString()}`;
        labels.push(timeLabel);
        oxygenLevels.push(oxygen);
      } else {
        const dayIndex = date.getDay();
        if (dayIndex >= 1) {
          dailyOxygenLevels[dayIndex - 1].push(oxygen);
        }
      }
    });

    const avgOxygenLevels = dailyOxygenLevels.map((oxygenArray) => {
      if (oxygenArray.length === 0) return 0;
      return (
        oxygenArray.reduce((sum, oxygen) => sum + oxygen, 0) /
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
            filter === "3hours" ? "Oxygen Every 3 Hours" : "Average Oxygen",
          data: filter === "3hours" ? oxygenLevels : avgOxygenLevels,
          fill: false,
          borderColor: "#00C2FF",
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
          filter === "3hours" ? "Oxygen Every 3 Hours" : "Weekly Oxygen Levels",
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

      {oxygenData.labels.length > 0 ? (
        <Line options={options} data={oxygenData} />
      ) : (
        <div>No data available to display</div>
      )}
    </div>
  );
};
