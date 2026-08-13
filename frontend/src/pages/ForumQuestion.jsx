import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getCurrentUser, getLocalRole } from "../services/auth";
import { createAnswer, deleteAnswer, deleteQuestion, getQuestion } from "../services/forum";

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

export default function ForumQuestion() {
  const { id } = useParams();
  const navigate = useNavigate();
  const user = getCurrentUser();
  const isAdmin = getLocalRole(user) === "admin";
  const [question, setQuestion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [body, setBody] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      setQuestion(await getQuestion(id));
    } catch (err) {
      setError(err.response?.data?.detail || "Question introuvable.");
      setQuestion(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const handleAnswer = async (e) => {
    e.preventDefault();
    if (!user) return;
    setSubmitting(true);
    setError("");
    try {
      await createAnswer(id, { body: body.trim(), author: user });
      setBody("");
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Échec de l'envoi de la réponse.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteQuestion = async () => {
    if (!window.confirm("Supprimer cette question et toutes ses réponses ?")) return;
    try {
      await deleteQuestion(id);
      navigate("/forum");
    } catch {
      setError("Impossible de supprimer la question.");
    }
  };

  const handleDeleteAnswer = async (answerId) => {
    if (!window.confirm("Supprimer cette réponse ?")) return;
    try {
      await deleteAnswer(answerId);
      await load();
    } catch {
      setError("Impossible de supprimer la réponse.");
    }
  };

  if (loading) return <p className="text-sm text-slate-400">Chargement…</p>;

  if (!question) {
    return (
      <div>
        <p className="text-sm text-red-700">{error || "Question introuvable."}</p>
        <Link to="/forum" className="mt-3 inline-block text-sm text-brand-700 hover:underline">
          ← Retour au forum
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <Link to="/forum" className="text-sm text-brand-700 hover:underline">
          ← Retour au forum
        </Link>
        {isAdmin && (
          <button type="button" onClick={handleDeleteQuestion} className="btn-secondary text-red-700">
            Supprimer la question
          </button>
        )}
      </div>

      <article className="card-surface p-5">
        <h1 className="font-display text-2xl font-semibold text-slate-800">{question.title}</h1>
        <p className="mt-1 text-xs text-slate-400">
          {question.author_name} · {formatDate(question.created_at)}
        </p>
        <p className="mt-4 whitespace-pre-wrap text-sm leading-relaxed text-slate-700">
          {question.body}
        </p>
      </article>

      {error && (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      <section className="space-y-3">
        <h2 className="font-display text-lg font-semibold text-slate-800">
          Réponses ({question.answers?.length || 0})
        </h2>
        {(question.answers || []).map((a) => (
          <article key={a.id} className="card-surface border-l-4 border-l-brand-500 p-4">
            <div className="flex items-start justify-between gap-3">
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-700">{a.body}</p>
              {isAdmin && (
                <button
                  type="button"
                  onClick={() => handleDeleteAnswer(a.id)}
                  className="shrink-0 text-xs text-red-600 hover:underline"
                >
                  Supprimer
                </button>
              )}
            </div>
            <p className="mt-3 text-xs text-slate-400">
              {a.author_name} · {formatDate(a.created_at)}
            </p>
          </article>
        ))}
      </section>

      <form onSubmit={handleAnswer} className="card-surface space-y-3 p-5">
        <h3 className="font-display text-base font-semibold text-slate-800">Votre réponse</h3>
        <textarea
          className="input-field min-h-[100px]"
          placeholder="Partagez votre réponse…"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          required
          minLength={1}
        />
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? "Envoi…" : "Répondre"}
        </button>
      </form>
    </div>
  );
}
