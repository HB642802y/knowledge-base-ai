import { Navigate } from "react-router-dom";
import { getCurrentUser, getLocalRole } from "../services/auth";

export default function PrivateRoute({ children, requireAdmin = false, requireCollaborator = false }) {
  const user = getCurrentUser();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && getLocalRole(user) !== "admin") {
    return <Navigate to="/collaborateur" replace />;
  }

  if (requireCollaborator && getLocalRole(user) === "admin") {
    return <Navigate to="/admin" replace />;
  }

  return children;
}
