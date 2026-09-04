import { useCallback, useEffect, useRef, useState } from "react";
import api from "../services/api";
import { createUser, deleteUser, listUsers, resetUserPassword } from "../services/users";
import { deleteDocument, listDocuments } from "../services/documents";
import { addChatComment, createChatQuestion, deleteChatQuestion, listChatQuestions } from "../services/chat";
import UploadForm from "../components/UploadForm";

const TABS = [
  { id: "users", label: "Utilisateurs" },
  { id: "stats", label: "Statistiques" },
  { id: "questions", label: "Questions IA" },
  { id: "upload", label: "Upload" },
];

function formatDate(value) {
  if (!value) return "recemment";
  try {
    return new Date(value).toLocaleString("fr-FR", { dateStyle: "medium", timeStyle: "short" });
  } catch {
    return value;
  }
}

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
          Gestion des comptes, documents, questions IA et statistiques.
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
      {tab === "stats" && <StatsTab showToast={showToast} />}
      {tab === "questions" && <QuestionsTab showToast={showToast} />}
      {tab === "upload" && <UploadTab showToast={showToast} />}
    </div>
  );
}

function UsersTab({ showToast }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [passwords, setPasswords] = useState({});
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
      });
      showToast("Compte collaborateur créé.");
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

  const handleResetPassword = async (userId) => {
    const newPassword = (passwords[userId] || "").trim();
    if (!newPassword) return;
    try {
      await resetUserPassword(userId, newPassword);
      setPasswords((current) => ({ ...current, [userId]: "" }));
      showToast("Mot de passe collaborateur modifie.");
    } catch (err) {
      showToast(err.response?.data?.detail || "Modification impossible.", "error");
    }
  };

  return (
    <div className="space-y-6">
      <div className="card-surface overflow-x-auto">
        <table className="w-full min-w-[780px] text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Nom</th>
              <th className="px-4 py-3">Rôle</th>
              <th className="px-4 py-3">Nouveau mot de passe</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-6 text-slate-400">Chargement...</td></tr>
            ) : (
              users.map((u) => (
                <tr key={u.id} className="border-b border-slate-100">
                  <td className="px-4 py-3 text-slate-500">{u.id}</td>
                  <td className="px-4 py-3">{u.email}</td>
                  <td className="px-4 py-3">{u.full_name}</td>
                  <td className="px-4 py-3 capitalize">{u.role}</td>
                  <td className="px-4 py-3">
                    {u.role === "collaborateur" && (
                      <div className="flex min-w-[260px] gap-2">
                        <input
                          className="input-field min-h-9 py-1.5 text-xs"
                          type="text"
                          placeholder="Nouveau mot de passe"
                          value={passwords[u.id] || ""}
                          onChange={(e) => setPasswords((current) => ({ ...current, [u.id]: e.target.value }))}
                        />
                        <button
                          type="button"
                          onClick={() => handleResetPassword(u.id)}
                          className="btn-secondary min-h-9 px-3 py-1 text-xs"
                          disabled={!passwords[u.id]?.trim()}
                        >
                          Modifier
                        </button>
                      </div>
                    )}
                  </td>
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
        <h2 className="font-display text-base font-semibold text-slate-800">Créer un compte collaborateur</h2>
        <input className="input-field" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="input-field" type="text" placeholder="Nom complet" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
        <input className="input-field" type="text" placeholder="Mot de passe" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={4} />
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Création..." : "Créer le compte collaborateur"}
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

  if (loading) return <p className="text-sm text-slate-400">Chargement...</p>;
  if (!stats) return null;

  const cards = [
    { label: "Documents", value: stats.documents },
    { label: "Utilisateurs", value: stats.users },
    { label: "Questions IA", value: stats.conversations },
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

function UploadTab({ showToast }) {
  const [uploadResult, setUploadResult] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadDocuments = useCallback(async () => {
    setLoading(true);
    try {
      setDocuments(await listDocuments());
    } catch {
      showToast("Impossible de charger les documents.", "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleUploadResult = async (result) => {
    setUploadResult(result);
    if (result?.ok) {
      showToast(`Document ${result.data.filename} uploadé avec succès`);
      await loadDocuments();
    }
  };

  const handleDeleteDocument = async (document) => {
    if (!window.confirm(`Supprimer le document "${document.title}" ?`)) return;
    try {
      await deleteDocument(document.id);
      showToast("Document supprime.");
      await loadDocuments();
    } catch (err) {
      showToast(err.response?.data?.detail || "Suppression impossible.", "error");
    }
  };

  return (
    <div className="space-y-6">
      <div className="card-surface p-5">
        <h2 className="font-display text-base font-semibold text-slate-800 mb-4">Ajouter un document</h2>
        <UploadForm onResult={handleUploadResult} />
        {uploadResult?.ok && (
          <div
            className={`mt-4 rounded-md border px-4 py-3 text-sm ${
              uploadResult.data.status === "uploaded_and_indexed"
                ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                : "border-amber-200 bg-amber-50 text-amber-900"
            }`}
          >
            <p className="font-semibold">{uploadResult.data.filename}</p>
            <p className="mt-1">Statut : {uploadResult.data.status}</p>
            {uploadResult.data.error && (
              <p className="mt-2 text-xs opacity-90">{uploadResult.data.error}</p>
            )}
          </div>
        )}
        {uploadResult && !uploadResult.ok && (
          <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {uploadResult.error}
          </p>
        )}
      </div>

      <div className="card-surface overflow-x-auto">
        <table className="w-full min-w-[520px] text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Document</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={3} className="px-4 py-6 text-slate-400">Chargement...</td>
              </tr>
            ) : documents.length > 0 ? (
              documents.map((document) => (
                <tr key={document.id} className="border-b border-slate-100">
                  <td className="px-4 py-3 text-slate-500">{document.id}</td>
                  <td className="px-4 py-3 font-medium text-slate-800">{document.title}</td>
                  <td className="px-4 py-3">
                    {document.can_delete && (
                      <button type="button" className="text-xs text-red-600 hover:underline" onClick={() => handleDeleteDocument(document)}>
                        Supprimer
                      </button>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={3} className="px-4 py-6 text-slate-400">Aucun document.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function QuestionsTab({ showToast }) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [comments, setComments] = useState({});

  const loadQuestions = useCallback(async () => {
    setLoading(true);
    try {
      setQuestions(await listChatQuestions());
    } catch {
      showToast("Impossible de charger les questions IA.", "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    loadQuestions();
  }, [loadQuestions]);

  const handleAsk = async (event) => {
    event.preventDefault();
    const text = question.trim();
    if (!text || asking) return;
    setAsking(true);
    try {
      const created = await createChatQuestion(text);
      setQuestions((current) => [created, ...current]);
      setQuestion("");
      showToast("Question envoyee a l'agent IA.");
    } catch (err) {
      showToast(err.response?.data?.detail || "Impossible de poser la question.", "error");
    } finally {
      setAsking(false);
    }
  };

  const handleComment = async (questionId) => {
    const body = (comments[questionId] || "").trim();
    if (!body) return;
    try {
      const comment = await addChatComment(questionId, body);
      setQuestions((current) =>
        current.map((item) =>
          item.id === questionId ? { ...item, comments: [...(item.comments || []), comment] } : item,
        ),
      );
      setComments((current) => ({ ...current, [questionId]: "" }));
      showToast("Reponse ajoutee.");
    } catch (err) {
      showToast(err.response?.data?.detail || "Impossible d'ajouter la reponse.", "error");
    }
  };

  const handleDeleteQuestion = async (item) => {
    if (!window.confirm("Supprimer cette question avec sa reponse IA et ses commentaires ?")) return;
    try {
      await deleteChatQuestion(item.id);
      setQuestions((current) => current.filter((question) => question.id !== item.id));
      showToast("Question supprimee.");
    } catch (err) {
      showToast(err.response?.data?.detail || "Suppression impossible.", "error");
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleAsk} className="card-surface space-y-3 p-5">
        <h2 className="font-display text-base font-semibold text-slate-800">
          Poser une question aux documents
        </h2>
        <textarea
          className="input-field min-h-[120px]"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="L'agent IA lit les documents indexes puis publie sa reponse dans le fil."
          required
        />
        <button type="submit" className="btn-primary" disabled={!question.trim() || asking}>
          {asking ? "Generation..." : "Poser la question"}
        </button>
      </form>

      <div className="space-y-4">
        {loading && <p className="text-sm text-slate-400">Chargement...</p>}
        {!loading && questions.length === 0 && <p className="text-sm text-slate-400">Aucune question.</p>}
        {questions.map((item) => (
          <article key={item.id} className="card-surface p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <h3 className="font-display text-base font-semibold text-slate-800">{item.question}</h3>
                <p className="mt-1 text-xs text-slate-400">
                  {item.author_name || "Utilisateur"} - {formatDate(item.created_at)}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-600">
                  {item.comments?.length || 0} reponse(s)
                </span>
                {item.can_delete && (
                  <button
                    type="button"
                    onClick={() => handleDeleteQuestion(item)}
                    className="rounded border border-red-200 px-2 py-1 text-xs font-semibold text-red-600 hover:bg-red-50"
                  >
                    Supprimer
                  </button>
                )}
              </div>
            </div>

            {item.ai_answer && (
              <div className="mt-4 rounded-md border border-violet-300/20 bg-violet-500/10 p-4">
                <p className="text-xs font-semibold uppercase text-violet-200">Reponse IA</p>
                <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-600">{item.ai_answer}</p>
                {item.sources?.length > 0 && (
                  <p className="mt-2 text-xs text-slate-400">
                    Sources: {item.sources.map((source) => source.filename).join(", ")}
                  </p>
                )}
              </div>
            )}

            <div className="mt-4 space-y-2">
              {item.comments?.length > 0 ? (
                item.comments.map((comment) => (
                  <div key={comment.id} className="rounded-md bg-slate-100 px-3 py-2">
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <p className="text-xs font-semibold text-slate-800">{comment.author_name}</p>
                      <p className="text-[11px] text-slate-400">{formatDate(comment.created_at)}</p>
                    </div>
                    <p className="mt-1 text-sm text-slate-600">{comment.body}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-400">Aucune reponse collaborateur.</p>
              )}
            </div>

            <div className="mt-4 flex gap-2 border-t border-slate-200 pt-4">
              <input
                className="input-field min-w-0 flex-1"
                value={comments[item.id] || ""}
                onChange={(event) => setComments((current) => ({ ...current, [item.id]: event.target.value }))}
                placeholder="Repondre a cette question"
              />
              <button type="button" className="btn-secondary" onClick={() => handleComment(item.id)} disabled={!comments[item.id]?.trim()}>
                Repondre
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}


