import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { APP_NAME, MINISTRY_FULL, MINISTRY_SHORT } from "../branding";
import MinistryLogo from "../components/MinistryLogo";
import { getCurrentUser, getHomePath, login } from "../services/auth";

export default function Login() {
  const navigate = useNavigate();
  const existing = getCurrentUser();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setEmail("");
    setPassword("");
  }, []);

  if (existing) {
    return <Navigate to={getHomePath(existing)} replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await login(email.trim(), password);
      navigate(getHomePath(user));
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || "Email ou mot de passe incorrect.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-6 flex justify-center">
            <MinistryLogo size="login" />
          </div>
          <p className="font-display text-2xl font-bold tracking-tight text-brand-800">
            {MINISTRY_SHORT}
          </p>
          <p className="mt-1 text-sm font-medium text-slate-600">{APP_NAME}</p>
          <p className="mx-auto mt-3 max-w-sm text-xs leading-relaxed text-slate-500">
            {MINISTRY_FULL}
          </p>
          <h1 className="mt-6 font-display text-xl font-semibold text-slate-800">
            Connexion
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="card-surface space-y-4 p-6 shadow-md" autoComplete="off">
          <input className="hidden" type="text" name="username" autoComplete="username" tabIndex={-1} aria-hidden="true" />
          <input className="hidden" type="password" name="password" autoComplete="current-password" tabIndex={-1} aria-hidden="true" />

          <div>
            <label htmlFor="email" className="mb-1 block text-sm font-medium text-slate-700">
              Email
            </label>
            <input
              id="email"
              name="sdsi-login-email"
              type="email"
              autoComplete="off"
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
              name="sdsi-login-password"
              type="password"
              autoComplete="new-password"
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
