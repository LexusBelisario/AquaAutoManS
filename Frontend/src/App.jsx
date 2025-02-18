import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import React, { useState, useEffect } from "react";
import Home from "./pages/Homepage";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/loginPage.jsx";
import Logs from "./pages/DataLogs.jsx";
import AboutUs from "./pages/AboutUs.jsx";
import { WebSocketProvider } from "./context/WebSocketContext";

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
              <WebSocketProvider>
                <Home setAuth={setAuth} />
              </WebSocketProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/logs"
          element={
            <ProtectedRoute auth={auth}>
              <WebSocketProvider>
                <Logs setAuth={setAuth} />
              </WebSocketProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/aboutus"
          element={
            <ProtectedRoute auth={auth}>
              <WebSocketProvider>
                <AboutUs setAuth={setAuth} />
              </WebSocketProvider>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}
