import { Navigate } from "react-router-dom";

/** Stub conservé : redirige vers le chat (page d'accueil produit). */
export default function Dashboard() {
  return <Navigate to="/chat" replace />;
}
