import { Navigate } from "react-router-dom";
import { getCurrentUser, getLocalRole } from "../services/auth";

export default function PrivateRoute({ children, requireAdmin = false }) {
  const user = getCurrentUser();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && getLocalRole(user) !== "admin") {
    return <Navigate to="/chat" replace />;
  }

  return children;
}
