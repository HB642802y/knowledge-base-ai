import { Link, NavLink, useNavigate } from "react-router-dom";
import { logout } from "../services/auth";

const mobileLink = ({ isActive }) =>
  [
    "rounded-md px-2.5 py-1.5 text-xs font-medium",
    isActive ? "bg-brand-50 text-brand-800" : "text-slate-600",
  ].join(" ");

export default function Navbar({ user, role }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="border-b border-slate-200/80 bg-white/90 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link to="/chat" className="group flex items-baseline gap-2">
          <span className="font-display text-xl font-bold tracking-tight text-brand-800">
            SDSI
          </span>
          <span className="hidden text-sm font-medium text-slate-500 sm:inline">
            Knowledge Base
          </span>
        </Link>

        {user && (
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-semibold text-slate-800">
                {user.full_name}
              </p>
              <p className="text-xs capitalize text-slate-500">{role}</p>
            </div>
            <button type="button" onClick={handleLogout} className="btn-secondary">
              Déconnexion
            </button>
          </div>
        )}
      </div>

      {user && (
        <nav className="flex gap-1 overflow-x-auto border-t border-slate-100 px-4 py-2 md:hidden">
          <NavLink to="/chat" className={mobileLink}>
            Chat
          </NavLink>
          <NavLink to="/documents" className={mobileLink}>
            Documents
          </NavLink>
          <NavLink to="/upload" className={mobileLink}>
            Upload
          </NavLink>
          {role === "admin" && (
            <NavLink to="/admin" className={mobileLink}>
              Admin
            </NavLink>
          )}
        </nav>
      )}
    </header>
  );
}
