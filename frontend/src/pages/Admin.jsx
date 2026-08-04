import { useCallback, useEffect, useRef, useState } from "react";
import api from "../services/api";

const TABS = [
  { id: "users", label: "Utilisateurs" },
  { id: "categories", label: "Catégories" },
  { id: "stats", label: "Statistiques" },
];

export default function Admin() {
  const [tab, setTab] = useState("users");
  const [toast, setToast] = useState(null);
  const toastTimer = useRef(null);

  const showToast = useCallback((message, type = "info") => {
    setToast({ message, type });
    if (toastTimer.current) window.clearTimeout(toastTimer.current);
    toastTimer.current = window.setTimeout(() => setToast(null), 4000);
  }, []);

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display text-2xl font-semibold text-slate-800">
          Administration
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Gestion des utilisateurs, catégories et statistiques (stubs backend).
        </p>
      </div>

      {toast && (
        <div
          className={`mb-4 rounded-md border px-4 py-3 text-sm ${
            toast.type === "error"
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-sky-200 bg-sky-50 text-sky-900"
          }`}
          role="status"
        >
          {toast.message}
        </div>
      )}

      <div className="mb-4 flex gap-1 border-b border-slate-200">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium transition ${
              tab === t.id
                ? "border-b-2 border-brand-600 text-brand-800"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "users" && <UsersTab showToast={showToast} />}
      {tab === "categories" && <CategoriesTab showToast={showToast} />}
      {tab === "stats" && <StatsTab showToast={showToast} />}
    </div>
  );
}

function UsersTab({ showToast }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/users/");
      setUsers(data);
    } catch {
      showToast("Impossible de charger les utilisateurs.", "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    load();
  }, [load]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post("/users/", { email: email.trim(), full_name: fullName.trim() });
      showToast(
        "Utilisateur « créé » — stub backend : rien n'est persisté en base pour l'instant."
      );
      setEmail("");
      setFullName("");
      await load();
    } catch {
      showToast("Échec de la création utilisateur.", "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="card-surface overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3 font-semibold">ID</th>
              <th className="px-4 py-3 font-semibold">Email</th>
              <th className="px-4 py-3 font-semibold">Nom</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={3} className="px-4 py-6 text-slate-400">
                  Chargement…
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr key={u.id} className="border-b border-slate-100 last:border-0">
                  <td className="px-4 py-3 text-slate-500">{u.id}</td>
                  <td className="px-4 py-3">{u.email}</td>
                  <td className="px-4 py-3">{u.full_name}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <form onSubmit={handleCreate} className="card-surface max-w-lg space-y-3 p-5">
        <h2 className="font-display text-base font-semibold text-slate-800">
          Nouvel utilisateur
        </h2>
        <p className="text-xs text-slate-500">
          POST /users/ est un stub : la réponse est un écho, sans persistance.
        </p>
        <input
          className="input-field"
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          className="input-field"
          type="text"
          placeholder="Nom complet"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Création…" : "Créer"}
        </button>
      </form>
    </div>
  );
}

function CategoriesTab({ showToast }) {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/categories/");
      setCategories(data);
    } catch {
      showToast("Impossible de charger les catégories.", "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    load();
  }, [load]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post("/categories/", {
        name: name.trim(),
        description: description.trim() || null,
      });
      showToast(
        "Catégorie « créée » — stub backend : rien n'est persisté en base pour l'instant."
      );
      setName("");
      setDescription("");
      await load();
    } catch {
      showToast("Échec de la création de catégorie.", "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-3 sm:grid-cols-2">
        {loading && <p className="text-sm text-slate-400">Chargement…</p>}
        {!loading &&
          categories.map((c) => (
            <article key={c.id} className="card-surface p-4">
              <h3 className="font-semibold text-slate-800">{c.name}</h3>
              <p className="mt-1 text-sm text-slate-500">
                {c.description || "—"}
              </p>
            </article>
          ))}
      </div>

      <form onSubmit={handleCreate} className="card-surface max-w-lg space-y-3 p-5">
        <h2 className="font-display text-base font-semibold text-slate-800">
          Nouvelle catégorie
        </h2>
        <p className="text-xs text-slate-500">
          POST /categories/ est un stub : la réponse est un écho, sans persistance.
        </p>
        <input
          className="input-field"
          type="text"
          placeholder="Nom"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <textarea
          className="input-field min-h-[80px]"
          placeholder="Description (optionnel)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Création…" : "Créer"}
        </button>
      </form>
    </div>
  );
}

function StatsTab({ showToast }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get("/admin/stats");
        setStats(data);
      } catch {
        showToast("Impossible de charger les statistiques.", "error");
      } finally {
        setLoading(false);
      }
    })();
  }, [showToast]);

  if (loading) {
    return <p className="text-sm text-slate-400">Chargement…</p>;
  }

  if (!stats) return null;

  const cards = [
    { label: "Documents", value: stats.documents },
    { label: "Utilisateurs", value: stats.users },
    { label: "Conversations", value: stats.conversations },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {cards.map((card) => (
        <div key={card.label} className="card-surface p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            {card.label}
          </p>
          <p className="mt-2 font-display text-3xl font-bold text-brand-800">
            {card.value}
          </p>
        </div>
      ))}
    </div>
  );
}
