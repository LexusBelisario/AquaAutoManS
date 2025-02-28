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

export const LineGraphOxygen = () => {
  const [oxygenData, setOxygenData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("weekly");
  const [selectedDate, setSelectedDate] = useState("");
  const [weekStart, setWeekStart] = useState("");
  const [cache, setCache] = useState({}); // Add cache state

  // Memoize the fetch function
  const fetchOxygenData = useCallback(async () => {
    try {
      // Create cache key based on current filter parameters
      const cacheKey = `${filter}-${selectedDate}-${weekStart}`;

      // Check if data exists in cache
      if (cache[cacheKey]) {
        setOxygenData(cache[cacheKey]);
        setLoading(false);
        return;
      }

      let url = `http://127.0.0.1:5000/filtered-oxygen-data?filter=${filter}`;

      if (filter === "date" && selectedDate) {
        url += `&selected_date=${selectedDate}`;
      } else if (filter === "week" && weekStart) {
        url += `&week_start=${weekStart}`;
      }

      setLoading(true);
      const response = await fetch(url);
      const data = await response.json();

      const processedData = processOxygenData(data);

      // Store in cache
      setCache((prevCache) => ({
        ...prevCache,
        [cacheKey]: processedData,
      }));

      setOxygenData(processedData);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching oxygen data:", error);
      setLoading(false);
    }
  }, [filter, selectedDate, weekStart, cache]);

  useEffect(() => {
    fetchOxygenData();
  }, [fetchOxygenData]);

  // Memoize the processing function
  const processOxygenData = useMemo(
    () => (data) => {
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
      const oxygenLevels = filter === "3hours" ? [] : [];

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
    },
    [filter]
  );

  // Memoize options
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
              ? "Oxygen Every 3 Hours"
              : "Weekly Oxygen Levels",
        },
      },
    }),
    [filter]
  );

  // Loading spinner component
  const LoadingSpinner = () => (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
    </div>
  );

  return (
    <div className="w-full max-w-screen-lg mx-auto">
      <div className="mb-4">
        <label>Filter: </label>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="ml-2 p-2 border rounded"
        >
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
            className="ml-2 p-2 border rounded"
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
            className="ml-2 p-2 border rounded"
          />
        </div>
      )}

      {loading ? (
        <LoadingSpinner />
      ) : oxygenData?.labels?.length > 0 ? (
        <Line options={options} data={oxygenData} />
      ) : (
        <div className="text-center py-4">No data available to display</div>
      )}
    </div>
  );
};
