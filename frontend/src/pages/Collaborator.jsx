import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { addChatComment, createChatQuestion, deleteChatQuestion, listChatQuestions } from "../services/chat";
import { getCurrentUser, getLocalRole } from "../services/auth";
import UploadForm from "../components/UploadForm";

function formatDate(value) {
  if (!value) return "recemment";
  try {
    return new Date(value).toLocaleString("fr-FR", { dateStyle: "medium", timeStyle: "short" });
  } catch {
    return value;
  }
}

function ReplyForm({ disabled, questionId, onReply }) {
  const [body, setBody] = useState("");
  const [sending, setSending] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    const text = body.trim();
    if (!text || disabled || sending) return;
    setSending(true);
    try {
      await onReply(questionId, text);
      setBody("");
    } finally {
      setSending(false);
    }
  };

  return (
    <form onSubmit={submit} className="mt-4 flex gap-2 border-t border-white/10 pt-4">
      <input
        className="input-field min-w-0 flex-1"
        value={body}
        onChange={(event) => setBody(event.target.value)}
        placeholder={disabled ? "Connectez-vous pour repondre" : "Ecrire une reponse"}
        disabled={disabled || sending}
      />
      <button type="submit" className="btn-secondary" disabled={disabled || !body.trim() || sending}>
        {sending ? "..." : "Repondre"}
      </button>
    </form>
  );
}

export default function Collaborator() {
  const user = getCurrentUser();
  const role = getLocalRole(user);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  const loadQuestions = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setQuestions(await listChatQuestions({ public: !user }));
    } catch (err) {
      setError(err.response?.data?.detail || "Impossible de charger les questions.");
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadQuestions();
  }, [loadQuestions]);

  const totalComments = useMemo(
    () => questions.reduce((total, question) => total + (question.comments?.length || 0), 0),
    [questions],
  );

  const handleReply = async (questionId, body) => {
    setError("");
    try {
      const comment = await addChatComment(questionId, body);
      setQuestions((current) =>
        current.map((question) =>
          question.id === questionId
            ? { ...question, comments: [...(question.comments || []), comment] }
            : question,
        ),
      );
    } catch (err) {
      setError(err.response?.data?.detail || "Impossible d'ajouter la reponse.");
    }
  };

  const handleAsk = async (event) => {
    event.preventDefault();
    const text = question.trim();
    if (!text || asking) return;
    setAsking(true);
    setError("");
    try {
      const created = await createChatQuestion(text);
      setQuestions((current) => [created, ...current]);
      setQuestion("");
    } catch (err) {
      setError(err.response?.data?.detail || "Impossible de poser la question.");
    } finally {
      setAsking(false);
    }
  };

  const handleDeleteQuestion = async (item) => {
    if (!window.confirm("Supprimer cette question avec sa reponse IA et ses commentaires ?")) return;
    setError("");
    try {
      await deleteChatQuestion(item.id);
      setQuestions((current) => current.filter((question) => question.id !== item.id));
    } catch (err) {
      setError(err.response?.data?.detail || "Suppression impossible.");
    }
  };

  return (
    <div className="dashboard max-w-5xl space-y-5">
      <header className="flex flex-wrap items-start justify-between gap-4 pt-1">
        <div>
          <p className="text-xs font-medium uppercase text-violet-300">
            {user ? `${user.full_name} - ${role}` : "Accueil public"}
          </p>
          <h1 className="mt-1 font-display text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
            Questions et commentaires
          </h1>
        </div>
        <div className="flex flex-wrap gap-2">
          {!user ? (
            <Link to="/login" className="btn-primary">Se connecter</Link>
          ) : (
            <Link to={role === "admin" ? "/admin" : "/settings"} className="btn-secondary">
              Compte {role}
            </Link>
          )}
        </div>
      </header>

      {error && <p className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

      <section className="grid gap-3 sm:grid-cols-2">
        <article className="card-surface p-4">
          <p className="text-xs font-semibold uppercase text-slate-400">Questions</p>
          <p className="mt-2 text-3xl font-extrabold tabular-nums text-white">{questions.length}</p>
        </article>
        <article className="card-surface p-4">
          <p className="text-xs font-semibold uppercase text-slate-400">Commentaires</p>
          <p className="mt-2 text-3xl font-extrabold tabular-nums text-white">{totalComments}</p>
        </article>
      </section>

      {user && (
        <section className="card-surface p-5">
          <h2 className="text-sm font-bold text-white">Poser une question aux documents</h2>
          <form onSubmit={handleAsk} className="mt-4 space-y-3">
            <textarea
              className="input-field min-h-[120px]"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Votre question sera traitee par l'agent IA puis partagee avec les collaborateurs."
              disabled={asking}
            />
            <button type="submit" className="btn-primary" disabled={!question.trim() || asking}>
              {asking ? "Generation..." : "Poser la question"}
            </button>
          </form>
        </section>
      )}

      {user && (
        <section className="card-surface p-5">
          <h2 className="text-sm font-bold text-white">Ajouter un document</h2>
          <div className="mt-4">
            <UploadForm onResult={setUploadResult} />
          </div>
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
        </section>
      )}

      <section className="card-surface p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-sm font-bold text-white">Fil des questions</h2>
          {user ? (
            <span className="text-xs text-slate-400">Vous pouvez repondre aux questions existantes.</span>
          ) : (
            <span className="text-xs text-slate-400">Questions et reponses publiees par les admins et collaborateurs.</span>
          )}
        </div>

        <div className="mt-5 space-y-4">
          {loading && <p className="text-sm text-slate-400">Chargement...</p>}
          {!loading && questions.length === 0 && (
            <p className="text-sm text-slate-400">Aucune question pour le moment.</p>
          )}

          {questions.map((item) => (
            <article key={item.id} className="rounded-lg border border-white/10 bg-white/[0.035] p-4">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="text-base font-semibold text-slate-100">{item.question}</p>
                  <p className="mt-1 text-[11px] text-slate-500">
                    {item.author_name || "Collaborateur"} - {formatDate(item.created_at)}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <span className="rounded bg-white/[0.08] px-2 py-1 text-[10px] text-slate-300">
                    {item.comments?.length || 0} commentaire(s)
                  </span>
                  {item.can_delete && (
                    <button
                      type="button"
                      onClick={() => handleDeleteQuestion(item)}
                      className="rounded border border-red-300/30 px-2 py-1 text-[10px] font-semibold text-red-200 hover:bg-red-500/10"
                    >
                      Supprimer
                    </button>
                  )}
                </div>
              </div>

              {item.ai_answer && (
                <div className="mt-4 rounded-md border border-violet-300/20 bg-violet-500/10 p-3">
                  <p className="text-[11px] font-semibold uppercase text-violet-200">Reponse IA</p>
                  <p className="mt-2 whitespace-pre-wrap text-xs leading-relaxed text-slate-300">{item.ai_answer}</p>
                  {item.sources?.length > 0 && (
                    <p className="mt-2 text-[11px] text-slate-500">
                      Sources: {item.sources.map((source) => source.filename).join(", ")}
                    </p>
                  )}
                </div>
              )}

              <div className="mt-4 space-y-2">
                {item.comments?.length > 0 ? (
                  item.comments.map((comment) => (
                    <div key={comment.id} className="rounded-md bg-black/15 px-3 py-2">
                      <div className="flex flex-wrap items-baseline justify-between gap-2">
                        <p className="text-[11px] font-semibold text-slate-200">{comment.author_name}</p>
                        <p className="text-[10px] text-slate-500">{formatDate(comment.created_at)}</p>
                      </div>
                      <p className="mt-1 text-xs text-slate-400">{comment.body}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-500">Aucun commentaire pour cette question.</p>
                )}
              </div>

              <ReplyForm disabled={!user} questionId={item.id} onReply={handleReply} />
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
