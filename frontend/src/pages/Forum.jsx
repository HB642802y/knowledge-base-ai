import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCurrentUser } from "../services/auth";
import { createQuestion, listQuestions } from "../services/forum";

function formatDate(value) {
  if (!value) return "";
  try {
    return new Date(value).toLocaleString("fr-FR", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return value;
  }
}

export default function Forum() {
  const user = getCurrentUser();
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      setQuestions(await listQuestions());
    } catch (err) {
      setError(err.response?.data?.detail || "Impossible de charger le forum.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!user) return;
    setSubmitting(true);
    setError("");
    try {
      await createQuestion({ title: title.trim(), body: body.trim(), author: user });
      setTitle("");
      setBody("");
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Échec de la publication.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-slate-800">
          Forum collaboratif
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Posez une question visible par les autres agents. Les réponses enrichissent
          aussi l&apos;assistant IA (documents + forum).
        </p>
      </div>

      {error && (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      <form onSubmit={handleCreate} className="card-surface space-y-3 p-5">
        <h2 className="font-display text-base font-semibold text-slate-800">
          Nouvelle question
        </h2>
        <input
          className="input-field"
          placeholder="Titre de la question"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          minLength={3}
        />
        <textarea
          className="input-field min-h-[110px]"
          placeholder="Décrivez votre question en détail…"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          required
          minLength={3}
        />
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Publication…" : "Publier"}
        </button>
      </form>

      <div className="space-y-3">
        {loading && <p className="text-sm text-slate-400">Chargement…</p>}
        {!loading && questions.length === 0 && (
          <p className="text-sm text-slate-400">
            Aucune question pour l&apos;instant. Soyez le premier à en poser une.
          </p>
        )}
        {questions.map((q) => (
          <Link
            key={q.id}
            to={`/forum/${q.id}`}
            className="card-surface block p-4 transition hover:border-brand-200"
          >
            <div className="flex items-start justify-between gap-3">
              <h3 className="font-display text-base font-semibold text-slate-800">
                {q.title}
              </h3>
              <span className="shrink-0 rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                {q.answers_count} réponse{q.answers_count === 1 ? "" : "s"}
              </span>
            </div>
            <p className="mt-2 line-clamp-2 text-sm text-slate-600">{q.body}</p>
            <p className="mt-3 text-xs text-slate-400">
              {q.author_name} · {formatDate(q.created_at)}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
