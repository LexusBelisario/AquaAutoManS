import React, { useEffect, useState } from "react";
import Navbar from "../components/NavBar";
import DataTable from "react-data-table-component";
import Sidebar from "../components/sideBar";
import axios from "axios";

export default function DataLogs({ setAuth }) {
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [filterDate, setFilterDate] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const columns = [
    {
      name: "Temperature",
      selector: (row) => row["temperature"],
      sortable: true,
      cell: (row) => (
        <div
          style={{
            color:
              (row.temperature <= 20 && row.temperature !== 0) ||
              row.temperature >= 35 ||
              row.temperature === 0 ||
              row.temperature < 0 ||
              (row.temperature >= 20 && row.temperature <= 26) ||
              (row.temperature >= 32 && row.temperature <= 35)
                ? "red"
                : "black",
            padding: "8px",
          }}
        >
          {row.temperature}
        </div>
      ),
    },
    {
      name: "Temperature Result",
      selector: (row) => row["tempResult"],
      sortable: true,
      cell: (row) => (
        <div
          style={{
            color:
              row.tempResult === "BelowAverageTemperature" ||
              row.tempResult === "ColdTemperature" ||
              row.tempResult === "AboveAverageTemperature" ||
              row.tempResult === "HotTemperature"
                ? "red"
                : "black",
            padding: "8px",
          }}
        >
          {row.tempResult}
        </div>
      ),
    },
    {
      name: "Oxygen",
      selector: (row) => row["oxygen"],
      sortable: true,
      cell: (row) => (
        <div
          style={{
            color:
              row.oxygen === 0 || row.oxygen < 1.5 || row.oxygen < 5
                ? "red"
                : "black",
            padding: "8px",
          }}
        >
          {row.oxygen}
        </div>
      ),
    },
    {
      name: "Oxygen Result",
      selector: (row) => row["oxygenResult"],
      sortable: true,
      cell: (row) => (
        <div
          style={{
            color:
              row.oxygenResult === "VeryLowOxygen" ||
              row.oxygenResult === "LowOxygen" ||
              row.oxygenResult === "HighOxygen"
                ? "red"
                : "black",
            padding: "8px",
          }}
        >
          {row.oxygenResult}
        </div>
      ),
    },
    {
      name: "pH Level",
      selector: (row) => row["phlevel"],
      sortable: true,
      cell: (row) => (
        <div
          style={{
            color:
              (row.phlevel >= 4 && row.phlevel < 6) ||
              row.phlevel < 4 ||
              (row.phlevel > 7 && row.phlevel <= 9) ||
              row.phlevel < 9
                ? "red"
                : "black",
            padding: "8px",
          }}
        >
          {row.phlevel}
        </div>
      ),
    },
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
    {
      name: "Alive Catfish",
      selector: (row) => row["catfish"],
      sortable: true,
    },
    {
      name: "Dead Catfish",
      selector: (row) => row["dead_catfish"],
      sortable: true,
    },
    { name: "Time", selector: (row) => row["timeData"], sortable: true },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        let url = "http://localhost:5000/data";
        if (filterDate) {
          url += `?date=${filterDate}`;
        }
        const response = await axios.get(url);
        
        // Ensure response.data.data is an array
        if (!Array.isArray(response.data.data)) {
          console.error("Error: Data is not an array!", response.data);
          return;
        }
  
        console.log("Fetched data array:", response.data.data); // Debugging log
  
        setData(response.data.data); // Use response.data.data instead of response.data
        applyFilter(response.data.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
  
    fetchData();
    const intervalId = setInterval(fetchData, 5000);
    return () => clearInterval(intervalId);
  }, [filterDate]);
  

  const applyFilter = (dataToFilter) => {
    if (!Array.isArray(dataToFilter)) {
      console.error("applyFilter received non-array data:", dataToFilter);
      return;
    }
  
    if (filterDate) {
      const formattedFilterDate = filterDate;
      const filtered = dataToFilter.filter((row) => {
        const rowDate = new Date(row.timeData).toISOString().split("T")[0];
        return rowDate === formattedFilterDate;
      });
  
      setFilteredData(filtered);
    } else {
      setFilteredData(dataToFilter);
    }
  };
  

  const handleDateChange = (e) => {
    const selectedDate = e.target.value;
    setFilterDate(selectedDate); // Update filterDate

    // Force reset of filtered data when a new date is selected
    setFilteredData([]); // Reset filtered data so it doesn't include outdated data

    if (selectedDate) {
      applyFilter(data); // Reapply the filter with the new date
    }
  };

  const handlePageChange = (page) => {
    setCurrentPage(page); // Update current page
  };

  const handleRowsPerPageChange = (newRowsPerPage) => {
    setRowsPerPage(newRowsPerPage); // Update rows per page
  };

  const generateReport = async (filterOption) => {
    let url = "http://localhost:5000/check_data/print";
    const today = new Date().toISOString().split("T")[0]; // Get today's date as YYYY-MM-DD

    // For "by_date" filter, check if a date is selected
    if (filterOption === "by_date" && filterDate) {
      // Ensure the date is valid and fetch data for that date
      const response = await axios.get(
        `http://localhost:5000/data?date=${filterDate}`
      );
      if (response.data.length === 0) {
        alert("No data found for the selected date.");
        return;
      }
      url += `?date=${filterDate}`;
    } else if (filterOption === "3_hours" && filterDate === today) {
      // Only apply 3 hours filter if the selected date is today's date
      url += "?hours=3";
    } else if (filterOption === "1_hour") {
      url += "?hours=1";
    }

    // If no date is selected and user tries to generate "by_date" report, show alert
    if (filterOption === "by_date" && !filterDate) {
      alert("Please select a date to generate the report.");
      return;
    }

    // Generate and download the report
    try {
      const response = await axios.get(url, { responseType: "blob" });
      const file = new Blob([response.data], { type: "application/pdf" });
      const fileURL = URL.createObjectURL(file);
      const link = document.createElement("a");
      link.href = fileURL;
      link.download = "data-report.pdf";
      link.click();
    } catch (error) {
      console.error("Error generating report:", error);
    }
  };

  return (
    <div className="min-h-screen bg-[#F0F8FF] overflow-hidden overflow-x-hidden">
      <Navbar setAuth={setAuth} />

      <div className="flex">
        <div className="fixed">
          <Sidebar setAuth={setAuth} />
        </div>

        <div className="flex-1 ml-64 p-4">
          <div className="mb-4">
            <label htmlFor="dateFilter" className="mr-2">
              Filter by Date:
            </label>
            <input
              type="date"
              id="dateFilter"
              value={filterDate}
              onChange={handleDateChange}
              className="border border-gray-300 rounded p-2"
            />
          </div>

          <div className="mb-4">
            <button
              onClick={() => generateReport("3_hours")}
              className="bg-blue-500 text-white px-4 py-2 rounded mr-2"
            >
              Generate 3 Hours Report
            </button>
            <button
              onClick={() => generateReport("1_hour")}
              className="bg-blue-500 text-white px-4 py-2 rounded mr-2"
            >
              Generate 1 Hour Report
            </button>
            <button
              onClick={() => generateReport("by_date")}
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              Generate Report By Date
            </button>
          </div>

          <div id="printable-table">
            <DataTable
              columns={columns}
              data={filteredData}
              pagination
              paginationPerPage={rowsPerPage}
              paginationRowsPerPageOptions={[10, 20, 30, 50]}
              onChangePage={handlePageChange}
              onChangeRowsPerPage={handleRowsPerPageChange}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
