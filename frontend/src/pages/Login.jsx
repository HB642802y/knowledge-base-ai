import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { getCurrentUser, login } from "../services/auth";

export default function Login() {
  const navigate = useNavigate();
  const existing = getCurrentUser();

  const [email, setEmail] = useState("admin@sdsi.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (existing) {
    return <Navigate to="/chat" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email.trim(), password);
      navigate("/chat");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || "Identifiants invalides ou serveur indisponible.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <p className="font-display text-3xl font-bold tracking-tight text-brand-800">
            SDSI
          </p>
          <p className="mt-1 text-sm text-slate-500">Knowledge Base</p>
          <h1 className="mt-6 font-display text-xl font-semibold text-slate-800">
            Connexion
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="card-surface space-y-4 p-6">
          <div>
            <label htmlFor="email" className="mb-1 block text-sm font-medium text-slate-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="username"
              className="input-field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-slate-700">
              Mot de passe
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          )}

          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? "Connexion…" : "Se connecter"}
          </button>
        </form>
      </div>
    </div>
  );
}
