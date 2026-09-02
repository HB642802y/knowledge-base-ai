import { Link, NavLink, useNavigate } from "react-router-dom";
import { APP_NAME, MINISTRY_FULL, MINISTRY_SHORT } from "../branding";
import MinistryLogo from "./MinistryLogo";
import { getHomePath, getLocalRole, logout } from "../services/auth";

const mobileLink = ({ isActive }) =>
  [
    "rounded-md px-2.5 py-1.5 text-xs font-medium",
    isActive ? "bg-brand-50 text-brand-800" : "text-slate-600",
  ].join(" ");

export default function Navbar({ user }) {
  const navigate = useNavigate();
  const role = getLocalRole(user);
  const homePath = user ? getHomePath(user) : "/login";

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <header className="border-b border-slate-200/80 bg-white/95 backdrop-blur-sm shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3.5 sm:px-6 lg:px-8">
        <Link to={homePath} className="min-w-0">
          <div className="flex items-center gap-4">
            <MinistryLogo size="nav" />
            <div className="min-w-0 border-l border-slate-200 pl-4">
              <p className="truncate font-display text-base font-bold tracking-tight text-brand-800 sm:text-lg">
                {MINISTRY_SHORT}
              </p>
              <p className="truncate text-xs font-medium text-slate-500">{APP_NAME}</p>
              <p className="mt-0.5 hidden text-[10px] leading-snug text-slate-400 lg:block">
                {MINISTRY_FULL}
              </p>
            </div>
          </div>
        </Link>

        {user && (
          <div className="flex shrink-0 items-center gap-3">
            <div className="hidden text-right sm:block">
              <p className="text-sm font-semibold text-slate-800">{user.full_name}</p>
              <p className="text-xs capitalize text-slate-500">{role}</p>
            </div>
            <Link to="/settings" className="btn-secondary hidden sm:inline-flex">
              Paramètres
            </Link>
            <button type="button" onClick={handleLogout} className="btn-secondary">
              Déconnexion
            </button>
          </div>
        )}
      </div>

      {user && (
        <nav className="flex gap-1 overflow-x-auto border-t border-slate-100 px-4 py-2 md:hidden">
          <NavLink to="/collaborateur" className={mobileLink}>Espace</NavLink>
          <NavLink to="/chat" className={mobileLink}>Chat</NavLink>
          <NavLink to="/documents" className={mobileLink}>Documents</NavLink>
          <NavLink to="/upload" className={mobileLink}>Upload</NavLink>
          <NavLink to="/settings" className={mobileLink}>Paramètres</NavLink>
          {role === "admin" && <NavLink to="/admin" className={mobileLink}>Admin</NavLink>}
        </nav>
      )}
    </header>
  );
}
