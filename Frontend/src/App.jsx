import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import React, { useState, useEffect } from "react";
import Home from "./pages/Homepage";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/loginPage.jsx";
import Logs from "./pages/DataLogs.jsx";

export default function App() {
  const [auth, setAuth] = useState(() => {
    const savedAuth = localStorage.getItem("auth");
    return savedAuth === "true";
  });

  useEffect(() => {
    localStorage.setItem("auth", auth);
  }, [auth]);

  return (
    <Router>
      <Routes>
        <Route path="" element={<Login setAuth={setAuth} />} />
        <Route
          path="/main"
          element={
            <ProtectedRoute auth={auth}>
              <Home setAuth={setAuth} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/logs"
          element={
            <ProtectedRoute auth={auth}>
              <Logs setAuth={setAuth} />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}
