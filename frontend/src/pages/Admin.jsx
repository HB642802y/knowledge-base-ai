import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import { createUser, deleteUser, listUsers } from "../services/users";
import { deleteQuestion, listQuestions } from "../services/forum";

const TABS = [
  { id: "users", label: "Utilisateurs" },
  { id: "forum", label: "Forum" },
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
        <h1 className="font-display text-2xl font-semibold text-slate-800">Administration</h1>
        <p className="mt-1 text-sm text-slate-500">
          Gestion des comptes, modération forum, catégories et statistiques.
        </p>
      </div>

      {toast && (
        <div
          className={`mb-4 rounded-md border px-4 py-3 text-sm ${
            toast.type === "error"
              ? "border-red-200 bg-red-50 text-red-700"
              : "border-sky-200 bg-sky-50 text-sky-900"
          }`}
        >
          {toast.message}
        </div>
      )}

      <div className="mb-4 flex flex-wrap gap-1 border-b border-slate-200">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium ${
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
      {tab === "forum" && <ForumTab showToast={showToast} />}
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
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("collaborateur");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setUsers(await listUsers());
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
      await createUser({
        email: email.trim(),
        full_name: fullName.trim(),
        password,
        role,
      });
      showToast("Utilisateur créé.");
      setEmail("");
      setFullName("");
      setPassword("");
      await load();
    } catch (err) {
      showToast(err.response?.data?.detail || "Échec de la création.", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm("Supprimer cet utilisateur ?")) return;
    try {
      await deleteUser(userId);
      showToast("Utilisateur supprimé.");
      await load();
    } catch (err) {
      showToast(err.response?.data?.detail || "Suppression impossible.", "error");
    }
  };

  return (
    <div className="space-y-6">
      <div className="card-surface overflow-x-auto">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Nom</th>
              <th className="px-4 py-3">Rôle</th>
              <th className="px-4 py-3">Mot de passe</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-6 text-slate-400">Chargement…</td></tr>
            ) : (
              users.map((u) => (
                <tr key={u.id} className="border-b border-slate-100">
                  <td className="px-4 py-3 text-slate-500">{u.id}</td>
                  <td className="px-4 py-3">{u.email}</td>
                  <td className="px-4 py-3">{u.full_name}</td>
                  <td className="px-4 py-3 capitalize">{u.role}</td>
                  <td className="px-4 py-3 font-mono text-xs">{u.password_plain || "—"}</td>
                  <td className="px-4 py-3">
                    <button
                      type="button"
                      onClick={() => handleDelete(u.id)}
                      className="text-xs text-red-600 hover:underline"
                    >
                      Supprimer
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <form onSubmit={handleCreate} className="card-surface max-w-lg space-y-3 p-5">
        <h2 className="font-display text-base font-semibold text-slate-800">Nouvel utilisateur</h2>
        <input className="input-field" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="input-field" type="text" placeholder="Nom complet" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
        <input className="input-field" type="text" placeholder="Mot de passe" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={4} />
        <select className="input-field" value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="collaborateur">Collaborateur</option>
          <option value="admin">Administrateur</option>
        </select>
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Création…" : "Créer le compte"}
        </button>
      </form>
    </div>
  );
}

function ForumTab({ showToast }) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setQuestions(await listQuestions());
    } catch {
      showToast("Impossible de charger le forum.", "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    load();
  }, [load]);

  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer cette question ?")) return;
    try {
      await deleteQuestion(id);
      showToast("Question supprimée.");
      await load();
    } catch {
      showToast("Suppression impossible.", "error");
    }
  };

  if (loading) return <p className="text-sm text-slate-400">Chargement…</p>;

  return (
    <div className="space-y-3">
      {questions.map((q) => (
        <article key={q.id} className="card-surface flex items-start justify-between gap-3 p-4">
          <div>
            <Link to={`/forum/${q.id}`} className="font-semibold text-brand-800 hover:underline">
              {q.title}
            </Link>
            <p className="mt-1 text-xs text-slate-400">
              {q.author_name} · {q.answers_count} réponse(s)
            </p>
          </div>
          <button type="button" onClick={() => handleDelete(q.id)} className="btn-secondary text-red-700">
            Supprimer
          </button>
        </article>
      ))}
      {questions.length === 0 && <p className="text-sm text-slate-400">Aucune question.</p>}
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
      await api.post("/categories/", { name: name.trim(), description: description.trim() || null });
      showToast("Catégorie créée (stub — non persistée en DB).");
      setName("");
      setDescription("");
      await load();
    } catch {
      showToast("Échec de la création.", "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-3 sm:grid-cols-2">
        {loading && <p className="text-sm text-slate-400">Chargement…</p>}
        {!loading && categories.map((c) => (
          <article key={c.id} className="card-surface p-4">
            <h3 className="font-semibold text-slate-800">{c.name}</h3>
            <p className="mt-1 text-sm text-slate-500">{c.description || "—"}</p>
          </article>
        ))}
      </div>
      <form onSubmit={handleCreate} className="card-surface max-w-lg space-y-3 p-5">
        <input className="input-field" placeholder="Nom" value={name} onChange={(e) => setName(e.target.value)} required />
        <textarea className="input-field min-h-[80px]" placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
        <button type="submit" className="btn-primary" disabled={submitting}>Créer</button>
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

  if (loading) return <p className="text-sm text-slate-400">Chargement…</p>;
  if (!stats) return null;

  const cards = [
    { label: "Documents", value: stats.documents },
    { label: "Utilisateurs", value: stats.users },
    { label: "Questions forum", value: stats.conversations },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {cards.map((card) => (
        <div key={card.label} className="card-surface p-5">
          <p className="text-xs font-semibold uppercase text-slate-400">{card.label}</p>
          <p className="mt-2 font-display text-3xl font-bold text-brand-800">{card.value}</p>
        </div>
      ))}
    </div>
  );
}
