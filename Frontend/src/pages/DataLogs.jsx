import React, { useEffect, useState, useCallback } from "react";
import Navbar from "../components/NavBar";
import DataTable from "react-data-table-component";
import Sidebar from "../components/sideBar";
import axios from "axios";

export default function DataLogs({ setAuth }) {
  const [pageData, setPageData] = useState({
    data: [],
    total: 0,
    loading: false,
    error: null,
  });
  const [filterDate, setFilterDate] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [isLoading, setIsLoading] = useState(false);

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
    {
      name: "Turbidity",
      selector: (row) => row["turbidity"],
      sortable: true,
    },
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
    {
      name: "Time",
      selector: (row) => row["timeData"],
      sortable: true,
    },
  ];

  const fetchData = useCallback(async () => {
    setPageData((prev) => ({ ...prev, loading: true }));
    try {
      const config = {
        params: {
          date: filterDate || null, // Send null if no date selected
          page: currentPage,
          per_page: rowsPerPage,
        },
      };

      const response = await axios.get("http://localhost:5000/data", config);

      if (response.data && response.data.data) {
        setPageData({
          data: response.data.data,
          total: response.data.total,
          loading: false,
          error: null,
        });
      } else {
        throw new Error("Invalid data format received from server");
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      let errorMessage = "An unexpected error occurred";

      if (error.response) {
        if (error.response.status === 404) {
          errorMessage = "No data found for the selected date";
        } else if (error.response.status === 400) {
          errorMessage = "Invalid date format";
        } else if (error.response.status === 500) {
          errorMessage = "Server error. Please try again later.";
        }
      } else if (error.request) {
        errorMessage = "Unable to connect to the server";
      }

      setPageData((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
        data: [],
        total: 0,
      }));
    }
  }, [filterDate, currentPage, rowsPerPage]);

  useEffect(() => {
    fetchData();
    // Reduced polling frequency to 30 seconds
    const intervalId = setInterval(fetchData, 30000);
    return () => clearInterval(intervalId);
  }, [fetchData]);

  const handleDateChange = (e) => {
    const selectedDate = e.target.value;
    setFilterDate(selectedDate);
    setCurrentPage(1); // Reset to first page when date changes
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleRowsPerPageChange = (newRowsPerPage) => {
    setRowsPerPage(newRowsPerPage);
    setCurrentPage(1); // Reset to first page when rows per page changes
  };

  const generateReport = async (filterOption) => {
    try {
      setIsLoading(true); // Show loading state
      let url = "http://localhost:5000/check_data/print";

      if (filterOption === "by_date" && !filterDate) {
        alert("Please select a date to generate the report.");
        return;
      }

      if (filterOption === "by_date" && filterDate) {
        url += `?date=${filterDate}`;
      } else if (filterOption === "3_hours") {
        url += "?hours=3";
      } else if (filterOption === "1_hour") {
        url += "?hours=1";
      }

      const response = await axios.get(url, {
        responseType: "blob",
        timeout: 300000, // 5 minute timeout
      });

      const blob = new Blob([response.data], { type: "text/csv" });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = `aquamans_report_${new Date()
        .toISOString()
        .slice(0, 10)}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error("Error generating report:", error);
      alert("Error generating report. Please try again.");
    } finally {
      setIsLoading(false); // Hide loading state
    }
  };

  return (
    <div className="min-h-screen bg-[#F0F8FF] overflow-hidden">
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
              disabled={isLoading}
            >
              {isLoading ? "Generating..." : "Generate 3 Hours Report"}
            </button>
            <button
              onClick={() => generateReport("1_hour")}
              className="bg-blue-500 text-white px-4 py-2 rounded mr-2"
              disabled={isLoading}
            >
              {isLoading ? "Generating..." : "Generate 1 Hour Report"}
            </button>
            <button
              onClick={() => generateReport("by_date")}
              className="bg-blue-500 text-white px-4 py-2 rounded"
              disabled={isLoading}
            >
              {isLoading ? "Generating..." : "Generate Report By Date"}
            </button>
          </div>

          {isLoading && (
            <div className="text-center py-4">
              Generating report, please wait...
            </div>
          )}

          <div id="printable-table">
            <DataTable
              columns={columns}
              data={pageData.data}
              pagination
              paginationServer
              paginationTotalRows={pageData.total}
              paginationPerPage={rowsPerPage}
              paginationDefaultPage={currentPage}
              onChangePage={handlePageChange}
              onChangeRowsPerPage={handleRowsPerPageChange}
              progressPending={pageData.loading}
              persistTableHead
              paginationRowsPerPageOptions={[10, 20, 30, 50]}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
