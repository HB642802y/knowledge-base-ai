import { useState } from "react";
import ChatBox from "../components/ChatBox";
import { askQuestion } from "../services/chat";

function Sources({ items }) {
  if (!items?.length) return null;
  return (
    <ul className="mt-3 space-y-1 border-t border-slate-200/80 pt-2 text-xs text-slate-500">
      <li className="font-semibold text-slate-600">Sources</li>
      {items.map((src, i) => (
        <li key={`${src.filename}-${i}`}>• {src.filename}</li>
      ))}
    </ul>
  );
}

function AnswerCard({ title, badgeClass, content, sources }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm leading-relaxed text-slate-800">
      <p className={`mb-2 inline-block rounded px-2 py-0.5 text-xs font-semibold ${badgeClass}`}>
        {title}
      </p>
      <p className="whitespace-pre-wrap">{content}</p>
      <Sources items={sources} />
    </div>
  );
}

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async (question) => {
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);
    try {
      const data = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          document_answer: data.document_answer,
          document_sources: data.document_sources || [],
          forum_answer: data.forum_answer,
          forum_sources: data.forum_sources || [],
          ai_answer: data.ai_answer,
          ai_sources: data.ai_sources || [],
        },
      ]);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || "Erreur réseau";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", error: true, content: `Impossible d'obtenir une réponse : ${detail}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <div className="mb-4">
        <h1 className="page-title">Assistant</h1>
        <p className="page-subtitle">
          Trois réponses : documents téléversés, forum collaboratif, et assistant IA (Groq).
        </p>
      </div>

      <div className="card-surface flex min-h-0 flex-1 flex-col">
        <div className="flex-1 space-y-4 overflow-y-auto p-4">
          {messages.length === 0 && (
            <p className="py-12 text-center text-sm text-slate-400">
              Posez une question ci-dessous.
            </p>
          )}

          {messages.map((msg, index) => {
            if (msg.role === "user") {
              return (
                <div
                  key={`user-${index}`}
                  className="ml-auto max-w-3xl rounded-lg bg-brand-600 px-4 py-3 text-sm text-white"
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              );
            }
            if (msg.error) {
              return (
                <div
                  key={`err-${index}`}
                  className="max-w-3xl rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
                >
                  {msg.content}
                </div>
              );
            }
            return (
              <div key={`asst-${index}`} className="max-w-3xl space-y-3">
                <AnswerCard
                  title="Réponse documents"
                  badgeClass="bg-amber-50 text-amber-900"
                  content={msg.document_answer}
                  sources={msg.document_sources}
                />
                <AnswerCard
                  title="Réponse forum"
                  badgeClass="bg-emerald-50 text-emerald-800"
                  content={msg.forum_answer}
                  sources={msg.forum_sources}
                />
                <AnswerCard
                  title="Réponse IA (API)"
                  badgeClass="bg-sky-50 text-sky-800"
                  content={msg.ai_answer}
                  sources={msg.ai_sources}
                />
              </div>
            );
          })}

          {loading && (
            <p className="text-sm text-slate-400">
              Recherche documents + forum + appel API…
            </p>
          )}
        </div>

        <div className="border-t border-slate-200 p-4">
          <ChatBox onSubmit={handleAsk} disabled={loading} />
        </div>
      </div>
    </div>
  );
}
