import { NavLink } from "react-router-dom";

const linkClass = ({ isActive }) =>
  [
    "block rounded-md px-3 py-2 text-sm font-medium transition",
    isActive
      ? "bg-brand-50 text-brand-800"
      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
  ].join(" ");

export default function Sidebar({ role }) {
  return (
    <aside className="hidden w-52 shrink-0 md:block">
      <nav className="card-surface sticky top-6 space-y-1 p-2">
        <NavLink to="/chat" className={linkClass}>
          Chat
        </NavLink>
        <NavLink to="/documents" className={linkClass}>
          Documents
        </NavLink>
        <NavLink to="/upload" className={linkClass}>
          Upload
        </NavLink>
        {role === "admin" && (
          <NavLink to="/admin" className={linkClass}>
            Administration
          </NavLink>
        )}
      </nav>
    </aside>
  );
}
