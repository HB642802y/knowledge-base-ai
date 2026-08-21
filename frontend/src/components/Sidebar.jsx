import { NavLink } from "react-router-dom";

const links = [
  { to: "/chat", label: "Assistant" },
  { to: "/forum", label: "Forum" },
  { to: "/documents", label: "Documents" },
  { to: "/upload", label: "Upload" },
  { to: "/settings", label: "Paramètres" },
  { to: "/admin", label: "Administration", adminOnly: true },
];

const linkClass = ({ isActive }) =>
  [
    "flex items-center gap-2 rounded-md px-3 py-2.5 text-sm font-medium transition",
    isActive
      ? "bg-brand-50 text-brand-800 ring-1 ring-brand-100"
      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
  ].join(" ");

export default function Sidebar({ role }) {
  return (
    <aside className="hidden w-56 shrink-0 md:block">
      <nav className="card-surface sticky top-6 space-y-0.5 p-2">
        <p className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Navigation
        </p>
        {links
          .filter((l) => !l.adminOnly || role === "admin")
          .map((l) => (
            <NavLink key={l.to} to={l.to} className={linkClass}>
              {l.label}
            </NavLink>
          ))}
      </nav>
    </aside>
  );
}
