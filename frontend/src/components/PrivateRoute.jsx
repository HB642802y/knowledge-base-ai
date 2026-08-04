import { Navigate } from "react-router-dom";
import { getCurrentUser, getLocalRole } from "../services/auth";

/**
 * Protège les routes : redirige vers /login si aucun user en localStorage.
 * requireAdmin = true → redirige vers /chat si le rôle local n'est pas admin.
 */
export default function PrivateRoute({ children, requireAdmin = false }) {
  const user = getCurrentUser();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && getLocalRole(user.email) !== "admin") {
    return <Navigate to="/chat" replace />;
  }

  return children;
}
