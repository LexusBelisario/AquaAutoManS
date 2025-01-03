import React from "react";
import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children, auth }) {
  if (!auth) {
    return <Navigate to="/login" />;
  }
  return children;
}
