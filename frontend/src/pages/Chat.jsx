import { useCallback, useEffect, useState } from "react";
import ChatBox from "../components/ChatBox";
import { addChatComment, createChatQuestion, listChatQuestions } from "../services/chat";

function formatDate(value) {
  return new Date(value).toLocaleString("fr-FR", { dateStyle: "medium", timeStyle: "short" });
}

function CommentForm({ questionId, onComment }) {
  const [body, setBody] = useState("");
  const [sending, setSending] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    const text = body.trim();
    if (!text || sending) return;
    setSending(true);
    try {
      await onComment(questionId, text);
      setBody("");
    } finally {
      setSending(false);
    }
  };

  return (
    <form onSubmit={submit} className="mt-4 flex gap-2 border-t border-slate-100 pt-3">
      <input className="input-field flex-1" value={body} onChange={(event) => setBody(event.target.value)} placeholder="Écrire un commentaire…" aria-label="Commentaire" disabled={sending} />
      <button className="btn-secondary" disabled={!body.trim() || sending}>{sending ? "Envoi…" : "Commenter"}</button>
    </form>
  );
}

function QuestionCard({ item, onComment }) {
  return (
    <article className="card-surface overflow-hidden">
      <div className="p-5">
        <p className="text-sm font-semibold text-slate-800">{item.author_name}</p>
        <p className="mt-0.5 text-xs text-slate-400">{formatDate(item.created_at)}</p>
        <p className="mt-3 whitespace-pre-wrap text-base text-slate-700">{item.question}</p>
      </div>

      <div className="border-y border-sky-100 bg-sky-50/70 p-5">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-700 text-xs font-bold text-white">IA</span>
          <p className="text-sm font-semibold text-brand-800">Réponse de l’assistant IA</p>
        </div>
        <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-slate-700">{item.ai_answer}</p>
        {item.sources?.length > 0 && <p className="mt-3 text-xs text-slate-500">Sources : {item.sources.map((source) => source.filename).join(", ")}</p>}
      </div>

      <div className="p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Commentaires des collaborateurs ({item.comments?.length || 0})</p>
        <div className="mt-3 space-y-3">
          {item.comments?.map((comment) => (
            <div key={comment.id} className="rounded-xl bg-slate-100 px-4 py-3">
              <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
                <p className="text-sm font-semibold text-slate-800">{comment.author_name}</p>
                <p className="text-xs text-slate-400">{formatDate(comment.created_at)}</p>
              </div>
              <p className="mt-1 whitespace-pre-wrap text-sm text-slate-700">{comment.body}</p>
            </div>
          ))}
          {!item.comments?.length && <p className="text-sm text-slate-400">Aucun commentaire pour le moment.</p>}
        </div>
        <CommentForm questionId={item.id} onComment={onComment} />
      </div>
    </article>
  );
}

export default function Chat() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setQuestions(await listChatQuestions());
    } catch (err) {
      setError(err.response?.data?.detail || "Impossible de charger les échanges.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleAsk = async (question) => {
    setSending(true);
    setError("");
    try {
      const created = await createChatQuestion(question);
      setQuestions((current) => [created, ...current]);
    } catch (err) {
      setError(err.response?.data?.detail || "Impossible d’envoyer la question.");
    } finally {
      setSending(false);
    }
  };

  const handleComment = async (questionId, body) => {
    try {
      const comment = await addChatComment(questionId, body);
      setQuestions((current) => current.map((item) => item.id === questionId ? { ...item, comments: [...(item.comments || []), comment] } : item));
    } catch (err) {
      setError(err.response?.data?.detail || "Impossible de publier le commentaire.");
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      <div>
        <h1 className="page-title">Assistant collaboratif</h1>
        <p className="page-subtitle">Posez une question à l’IA, puis enrichissez la réponse avec les commentaires de vos collègues.</p>
      </div>
      <div className="card-surface p-4"><ChatBox onSubmit={handleAsk} disabled={sending} /></div>
      {error && <p className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
      {loading && <p className="text-center text-sm text-slate-400">Chargement des échanges…</p>}
      {!loading && questions.length === 0 && <p className="py-10 text-center text-sm text-slate-400">Soyez le premier à poser une question.</p>}
      {questions.map((item) => <QuestionCard key={item.id} item={item} onComment={handleComment} />)}
    </div>
  );
}
