import React from "react";
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

export const TrendGraph = ({ data, parameter }) => {
  const thresholds = PARAMETER_THRESHOLDS[parameter];

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: `${parameter.charAt(0).toUpperCase() + parameter.slice(1)} Trend`,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: (context) => {
            if (
              context.tick.value === thresholds.normal_low ||
              context.tick.value === thresholds.normal_high
            ) {
              return "rgba(0, 255, 0, 0.2)";
            }
            if (
              context.tick.value === thresholds.warning_low ||
              context.tick.value === thresholds.warning_high
            ) {
              return "rgba(255, 165, 0, 0.2)";
            }
            if (
              context.tick.value === thresholds.critical_low ||
              context.tick.value === thresholds.critical_high
            ) {
              return "rgba(255, 0, 0, 0.2)";
            }
            return "rgba(0, 0, 0, 0.1)";
          },
        },
      },
    },
  };

  return <Line options={options} data={data} />;
};
