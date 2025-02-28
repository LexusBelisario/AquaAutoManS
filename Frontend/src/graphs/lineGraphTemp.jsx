import React, { useEffect, useState, useCallback, useMemo } from "react";
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
  const [filter, setFilter] = useState("weekly");
  const [selectedDate, setSelectedDate] = useState("");
  const [weekStart, setWeekStart] = useState("");
  const [cache, setCache] = useState({});

  const processTemperatureData = useMemo(
    () => (data) => {
      console.log("Processing data:", data); // Debug log

      if (!Array.isArray(data) || data.length === 0) {
        console.log("No data to process");
        return {
          labels: [],
          datasets: [],
        };
      }

      if (filter === "3hours") {
        const labels = [];
        const temperatures = [];

        data.forEach((entry) => {
          const date = new Date(entry.timeData);
          const timeLabel = `${date.getHours()}:00 ${date.toLocaleDateString()}`;
          labels.push(timeLabel);
          temperatures.push(entry.temperature);
        });

        return {
          labels,
          datasets: [
            {
              label: "Temperature Every 3 Hours",
              data: temperatures,
              fill: false,
              borderColor: "#FF5F1F",
              tension: 0.1,
            },
          ],
        };
      } else {
        // For weekly view
        const dailyData = {
          0: [], // Monday
          1: [], // Tuesday
          2: [], // Wednesday
          3: [], // Thursday
          4: [], // Friday
          5: [], // Saturday
          6: [], // Sunday
        };

        // Group data by day
        data.forEach((entry) => {
          const date = new Date(entry.timeData);
          // Convert Sunday (0) to 6, and other days to 0-5
          const dayIndex = (date.getDay() + 6) % 7;
          if (entry.temperature != null) {
            dailyData[dayIndex].push(entry.temperature);
          }
        });

        console.log("Grouped daily data:", dailyData); // Debug log

        // Calculate averages
        const avgTemperatures = Object.values(dailyData).map((temps) => {
          if (temps.length === 0) return 0;
          const sum = temps.reduce((acc, temp) => acc + temp, 0);
          return parseFloat((sum / temps.length).toFixed(2));
        });

        console.log("Calculated averages:", avgTemperatures); // Debug log

        return {
          labels: [
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
              label: "Average Temperature",
              data: avgTemperatures,
              fill: false,
              borderColor: "#FF5F1F",
              tension: 0.1,
            },
          ],
        };
      }
    },
    [filter]
  );

  const fetchTemperatureData = useCallback(async () => {
    try {
      const cacheKey = `${filter}-${selectedDate}-${weekStart}`;

      if (cache[cacheKey]) {
        console.log("Using cached data for:", cacheKey);
        setTemperatureData(cache[cacheKey]);
        setLoading(false);
        return;
      }

      let url = `http://127.0.0.1:5000/filtered-temperature-data?filter=${filter}`;

      if (filter === "date" && selectedDate) {
        url += `&selected_date=${selectedDate}`;
      } else if (filter === "week" && weekStart) {
        url += `&week_start=${weekStart}`;
      }

      console.log("Fetching data from:", url); // Debug log

      setLoading(true);
      const response = await fetch(url);
      const data = await response.json();

      console.log("Raw data from API:", data); // Debug log

      if (!Array.isArray(data)) {
        console.error("Invalid data format received:", data);
        setLoading(false);
        return;
      }

      const processedData = processTemperatureData(data);
      console.log("Processed data:", processedData); // Debug log

      setCache((prevCache) => ({
        ...prevCache,
        [cacheKey]: processedData,
      }));

      setTemperatureData(processedData);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching temperature data:", error);
      setLoading(false);
    }
  }, [filter, selectedDate, weekStart, cache, processTemperatureData]);

  useEffect(() => {
    fetchTemperatureData();
  }, [fetchTemperatureData]);

  const options = useMemo(
    () => ({
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
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `${value}°C`,
          },
        },
      },
    }),
    [filter]
  );

  const LoadingSpinner = () => (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
    </div>
  );

  return (
    <div className="w-full max-w-screen-lg mx-auto p-4">
      <div className="mb-4">
        <label className="mr-2">Filter: </label>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="p-2 border rounded"
        >
          <option value="weekly">Weekly</option>
          <option value="3hours">Every 3 Hours</option>
          <option value="date">By Date</option>
          <option value="week">By Week</option>
        </select>
      </div>

      {filter === "date" && (
        <div className="mb-4">
          <label className="mr-2">Select Date: </label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="p-2 border rounded"
          />
        </div>
      )}

      {filter === "week" && (
        <div className="mb-4">
          <label className="mr-2">Select Week Start (Sunday): </label>
          <input
            type="date"
            value={weekStart}
            onChange={(e) => setWeekStart(e.target.value)}
            className="p-2 border rounded"
          />
        </div>
      )}

      {loading ? (
        <LoadingSpinner />
      ) : temperatureData?.labels?.length > 0 ? (
        <div className="bg-white p-4 rounded-lg shadow">
          <Line options={options} data={temperatureData} />
        </div>
      ) : (
        <div className="text-center py-4 text-gray-600">
          No data available to display
        </div>
      )}
    </div>
  );
};
