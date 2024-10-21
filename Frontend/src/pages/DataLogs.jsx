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
        const response = await axios.get("http://localhost:5000/data");
        setData(response.data);
        applyFilter(response.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 5000);

    return () => clearInterval(intervalId);
  }, [filterDate]);

  const applyFilter = (dataToFilter) => {
    if (filterDate) {
      const filtered = dataToFilter.filter((row) => {
        const rowDate = new Date(row.timeData).toISOString().split("T")[0];
        return rowDate === filterDate;
      });
      setFilteredData(filtered);
    } else {
      setFilteredData(dataToFilter);
    }
  };

  const handleDateChange = (e) => {
    const selectedDate = e.target.value;
    setFilterDate(selectedDate);
    applyFilter(data);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleRowsPerPageChange = (newRowsPerPage) => {
    setRowsPerPage(newRowsPerPage);
  };

  const handlePrint = () => {
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    const rowsToPrint = filteredData.slice(startIndex, endIndex);

    const printWindow = window.open("", "", "height=600,width=800");
    printWindow.document.write("<html><head><title>Print Table</title>");
    printWindow.document.write("</head><body>");
    printWindow.document.write("<h1>Data Logs</h1>");
    printWindow.document.write(
      '<table border="1" style="border-collapse: collapse;">'
    );
    printWindow.document.write("<thead><tr>");

    columns.forEach((column) => {
      printWindow.document.write(`<th>${column.name}</th>`);
    });

    printWindow.document.write("</tr></thead><tbody>");
    rowsToPrint.forEach((row) => {
      printWindow.document.write("<tr>");
      columns.forEach((column) => {
        const cellData = column.selector(row);
        let cellColor = "black";

        // Check temperature conditions
        if (
          column.name === "Temperature" &&
          ((row.temperature <= 20 && row.temperature !== 0) ||
            row.temperature >= 35 ||
            row.temperature === 0 ||
            row.temperature < 0 ||
            (row.temperature >= 20 && row.temperature <= 26) ||
            (row.temperature >= 32 && row.temperature <= 35))
        ) {
          cellColor = "red";
        }
        if (
          column.name === "Temperature Result" &&
          (row.tempResult === "BelowAverageTemperature" ||
            row.tempResult === "ColdTemperature" ||
            row.tempResult === "AboveAverageTemperature" ||
            row.tempResult === "HotTemperature")
        ) {
          cellColor = "red";
        }
        // Check oxygen conditions
        if (
          column.name === "Oxygen" &&
          (row.oxygen === 0 || row.oxygen < 1.5 || row.oxygen < 5)
        ) {
          cellColor = "red";
        }

        if (
          column.name === "Oxygen Result" &&
          (row.oxygenResult === "VeryLowOxygen" ||
            row.oxygenResult === "LowOxygen" ||
            row.oxygenResult === "HighOxygen")
        ) {
          cellColor = "red";
        }
        // Check pH level conditions
        if (
          column.name === "pH Level" &&
          ((row.phlevel >= 4 && row.phlevel < 6) ||
            row.phlevel < 4 ||
            (row.phlevel > 7 && row.phlevel <= 9) ||
            row.phlevel < 9)
        ) {
          cellColor = "red";
        }

        printWindow.document.write(
          `<td style="color: ${cellColor}; padding: 8px;">${cellData}</td>`
        );
      });
      printWindow.document.write("</tr>");
    });
    printWindow.document.write("</tbody></table>");
    printWindow.document.write("</body></html>");
    printWindow.document.close();
    printWindow.focus();
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

          <button
            type="button"
            className="text-purple-700 hover:text-white border border-purple-700 hover:bg-purple-800 focus:ring-4 focus:outline-none focus:ring-purple-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center mb-2 dark:border-purple-400 dark:text-purple-400 dark:hover:text-white dark:hover:bg-purple-500 dark:focus:ring-purple-900"
            onClick={handlePrint}
          >
            Print Current Page
          </button>

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
