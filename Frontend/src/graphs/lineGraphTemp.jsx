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
  const [error, setError] = useState(null);

  const processTemperatureData = useMemo(
    () => (data) => {
      console.log("Raw data received:", data);

      if (!Array.isArray(data) || data.length === 0) {
        console.log("No data to process or invalid data format");
        return {
          labels: [],
          datasets: [],
        };
      }

      // Create a map to store data by day
      const dailyData = new Map();
      const dayLabels = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
      ];

      if (filter === "3hours") {
        // Process 3-hour data
        const labels = [];
        const temperatures = [];

        data.forEach((entry) => {
          if (entry.temperature != null) {
            const date = new Date(entry.timeData);
            const timeLabel = `${date.getHours()}:00 ${date.toLocaleDateString()}`;
            labels.push(timeLabel);
            temperatures.push(parseFloat(entry.temperature));
          }
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
        // Process weekly/daily data
        data.forEach((entry) => {
          if (entry.temperature != null) {
            const date = new Date(entry.timeData);
            const dayIndex = (date.getDay() + 6) % 7; // Convert Sunday (0) to 6
            const dayName = dayLabels[dayIndex];

            if (!dailyData.has(dayName)) {
              dailyData.set(dayName, []);
            }
            dailyData.get(dayName).push(parseFloat(entry.temperature));
          }
        });

        // Calculate averages for each day
        const averages = dayLabels.map((day) => {
          const temperatures = dailyData.get(day) || [];
          if (temperatures.length === 0) return 0;
          const sum = temperatures.reduce((acc, val) => acc + val, 0);
          return parseFloat((sum / temperatures.length).toFixed(2));
        });

        console.log("Processed daily averages:", {
          labels: dayLabels,
          averages: averages,
        });

        return {
          labels: dayLabels,
          datasets: [
            {
              label: "Average Temperature",
              data: averages,
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
      setError(null);
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

      console.log("Fetching data from:", url);
      setLoading(true);

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Data received from API:", data);

      if (data.error) {
        throw new Error(data.error);
      }

      const processedData = processTemperatureData(data);
      console.log("Processed temperature data:", processedData);

      setCache((prevCache) => ({
        ...prevCache,
        [cacheKey]: processedData,
      }));

      setTemperatureData(processedData);
    } catch (error) {
      console.error("Error fetching temperature data:", error);
      setError(error.message);
    } finally {
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
          font: {
            size: 16,
          },
        },
        tooltip: {
          callbacks: {
            label: (context) => `Temperature: ${context.raw}°C`,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Temperature (°C)",
          },
          ticks: {
            callback: (value) => `${value}°C`,
          },
        },
        x: {
          title: {
            display: true,
            text: filter === "3hours" ? "Time" : "Day of Week",
          },
        },
      },
      interaction: {
        intersect: false,
        mode: "index",
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
      <div className="mb-4 flex items-center gap-4">
        <div>
          <label className="mr-2 font-medium">Filter: </label>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="p-2 border rounded hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="weekly">Weekly</option>
            <option value="3hours">Every 3 Hours</option>
            <option value="date">By Date</option>
            <option value="week">By Week</option>
          </select>
        </div>

        {filter === "date" && (
          <div>
            <label className="mr-2 font-medium">Select Date: </label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="p-2 border rounded hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}

        {filter === "week" && (
          <div>
            <label className="mr-2 font-medium">Select Week Start: </label>
            <input
              type="date"
              value={weekStart}
              onChange={(e) => setWeekStart(e.target.value)}
              className="p-2 border rounded hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          Error: {error}
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow-lg">
        {loading ? (
          <LoadingSpinner />
        ) : temperatureData?.labels?.length > 0 ? (
          <Line options={options} data={temperatureData} />
        ) : (
          <div className="text-center py-4 text-gray-600">
            No temperature data available for the selected period
          </div>
        )}
      </div>
    </div>
  );
};
