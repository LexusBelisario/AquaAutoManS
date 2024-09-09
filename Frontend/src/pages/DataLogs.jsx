import React, { useEffect, useState } from "react";
import Navbar from "../components/NavBar";
import DataTable from "react-data-table-component";
import Sidebar from "../components/sideBar";

import axios from "axios";

export default function DataLogs({ setAuth }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:5000/data");
        console.log("API Response:", response.data); // Log entire response
        setData(response.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 5000); // Fetch new data every 5 seconds

    return () => clearInterval(intervalId); // Cleanup on component unmount
  }, []);

  const columns = [
    {
      name: "Temperature",
      selector: (row) => row["temperature"],
      sortable: true,
    },
    {
      name: "Temperature Result",
      selector: (row) => row["tempResult"],
      sortable: true,
    },
    { name: "Oxygen", selector: (row) => row["oxygen"], sortable: true },
    {
      name: "Oxygen Result",
      selector: (row) => row["oxygenResult"],
      sortable: true,
    },
    { name: "pH Level", selector: (row) => row["phlevel"], sortable: true },
    {
      name: "pH Level Result",
      selector: (row) => row["phResult"],
      sortable: true,
    },
    { name: "Turbidity", selector: (row) => row["turbidity"], sortable: true },
    {
      name: "Turbidity Result",
      selector: (row) => row["turbidityResult"],
      sortable: true,
    },
    { name: "Time", selector: (row) => row["timeData"], sortable: true },
  ];

  return (
    <div className="min-h-screen bg-[#F0F8FF] overflow-hidden overflow-x-hidden">
      {/* Navbar at the top */}
      <Navbar setAuth={setAuth} />

      {/* Main content container */}
      <div className="flex">
        {/* Sidebar */}
        <div className="fixed">
          <Sidebar setAuth={setAuth} />
        </div>

        {/* Main content area */}
        <div className="flex-1 ml-64 p-4">
          <DataTable columns={columns} data={data} pagination />
        </div>
      </div>
    </div>
  );
}
