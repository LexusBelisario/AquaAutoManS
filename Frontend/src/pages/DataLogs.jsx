import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import DataTable from "react-data-table-component";
import Navbar from "../components/NavBar";
import Sidebar from "../components/sideBar";

export default function DataLogs({ setAuth }) {
  // Data and filtering states
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [filterDate, setFilterDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalRecords, setTotalRecords] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(100);

  // Download states
  const [downloadLoading, setDownloadLoading] = useState(false);

  // Columns definition
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
      sortable: true 
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
      sortable: true 
    },
  ];

  // Create axios instance
  const createAxiosInstance = useCallback(() => {
    return axios.create({
      baseURL: 'http://localhost:5000',
      timeout: 30000, // 30 seconds timeout
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
  }, []);

  // Fetch data function with pagination
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Create axios instance
      const axiosInstance = createAxiosInstance();

      // Construct URL with pagination parameters
      const url = filterDate 
        ? `/data?date=${filterDate}&page=${currentPage}&per_page=${rowsPerPage}` 
        : `/data?page=${currentPage}&per_page=${rowsPerPage}`;

      console.log("Fetching data from URL:", url);

      // Perform request
      const response = await axiosInstance.get(url);

      // Log full response
      console.log("Full API Response:", response.data);

      // Extract data and pagination info
      const { 
        data: fetchedData, 
        total, 
        page, 
        per_page, 
        total_pages 
      } = response.data;

      // Validate fetched data
      if (!Array.isArray(fetchedData)) {
        throw new Error("Received invalid data format");
      }

      // Update states
      setData(fetchedData);
      setFilteredData(fetchedData);
      setTotalRecords(total);
      setCurrentPage(page);
      setTotalPages(total_pages);

    } catch (error) {
      // Error handling
      console.error("Fetch Error:", error);
      
      const errorMessage = error.response?.data?.message || 
                           error.response?.data?.error || 
                           error.message || 
                           "An unexpected error occurred";

      setError(`Error: ${errorMessage}`);
      
      // Reset data
      setData([]);
      setFilteredData([]);
    } finally {
      setLoading(false);
    }
  }, [filterDate, currentPage, rowsPerPage, createAxiosInstance]);

  // Report generation function
  const generateReport = useCallback(async (filterOption) => {
    setDownloadLoading(true);
    
    try {
      let url = "http://localhost:5000/check_data/print";
      const today = new Date().toISOString().split('T')[0];

      // Determine report type
      if (filterOption === 'by_date' && filterDate) {
        // Validate date
        url += `?date=${filterDate}`;
      } else if (filterOption === '3_hours' && filterDate === today) {
        url += "?hours=3";
      } else if (filterOption === '1_hour') {
        url += "?hours=1";
      }

      // Perform download
      const response = await axios.get(url, {
        responseType: 'blob',
        timeout: 30000 // 30 seconds timeout
      });

      // Create download link
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `data_report_${filterOption}.xlsx`;
      link.click();

    } catch (error) {
      console.error("Report generation error:", error);
      
      // Error handling
      const errorMessage = error.response?.data?.message || 
                           error.response?.data?.error || 
                           error.message || 
                           "An unexpected error occurred";

      alert(`Failed to generate report: ${errorMessage}`);
    } finally {
      setDownloadLoading(false);
    }
  }, [filterDate]);

  // Initial and periodic data fetching
  useEffect(() => {
    fetchData();
    
    // Background refresh
    const intervalId = setInterval(fetchData, 60000); // 1 minute

    return () => {
      clearInterval(intervalId);
    };
  }, [fetchData]);

  // Network status monitoring
  useEffect(() => {
    const checkNetworkStatus = () => {
      console.log('Network status:', {
        online: navigator.onLine,
        connection: navigator.connection
      });

      if (!navigator.onLine) {
        setError("No internet connection. Please check your network.");
      }
    };

    // Add event listeners
    window.addEventListener('online', checkNetworkStatus);
    window.addEventListener('offline', checkNetworkStatus);

    return () => {
      window.removeEventListener('online', checkNetworkStatus);
      window.removeEventListener('offline', checkNetworkStatus);
    };
  }, []);

  // Pagination handlers
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleRowsPerPageChange = (newRowsPerPage) => {
    setRowsPerPage(newRowsPerPage);
  };

  // Date change handler
  const handleDateChange = (e) => {
    const selectedDate = e.target.value;
    
    // Validate date format
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(selectedDate)) {
      setError("Invalid date format");
      return;
    }
    
    setFilterDate(selectedDate);
    setCurrentPage(1); // Reset to first page when date changes
  };

  // Render method
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

          {/* Report Generation Buttons */}
          <div className="mb-4 flex space-x-2">
            <button
              onClick={() => generateReport("3_hours")}
              disabled={downloadLoading}
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              {downloadLoading ? 'Generating...' : 'Generate 3 Hours Report'}
            </button>
            <button
              onClick={() => generateReport("1_hour")}
              disabled={downloadLoading}
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              {downloadLoading ? 'Generating...' : 'Generate 1 Hour Report'}
            </button>
            <button
              onClick={() => generateReport("by_date")}
              disabled={downloadLoading || !filterDate}
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              {downloadLoading ? 'Generating...' : 'Generate Report By Date'}
            </button>
          </div>

          {/* Loading state */}
          {loading && (
            <div className="text-center py-4">
              <p>Loading data...</p>
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="text-center text-red-500 py-4">
              <p>Error: {error}</p>
            </div>
          )}

          {/* Data table */}
          {!loading && !error && (
            <div>
              <DataTable
                columns={columns}
                data={filteredData}
                pagination
                paginationServer
                paginationTotalRows={totalRecords}
                paginationPerPage={rowsPerPage}
                onChangePage={handlePageChange}
                onChangeRowsPerPage={handleRowsPerPageChange}
                paginationComponent={() => (
                  <div className="flex justify-between items-center p-2">
                    <span>
                      Page {currentPage} of {totalPages} (Total: {totalRecords} records)
                    </span>
                  </div>
                )}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}