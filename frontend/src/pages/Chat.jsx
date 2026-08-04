import { useState } from "react";
import ChatBox from "../components/ChatBox";
import { askQuestion } from "../services/chat";

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
          content: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || "Erreur réseau";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Impossible d'obtenir une réponse : ${detail}`,
          sources: [],
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <div className="mb-4">
        <h1 className="font-display text-2xl font-semibold text-slate-800">
          Assistant SDSI
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Interrogez la base documentaire. L&apos;historique reste local à cette session.
        </p>
      </div>

      <div className="card-surface flex min-h-0 flex-1 flex-col">
        <div className="flex-1 space-y-4 overflow-y-auto p-4">
          {messages.length === 0 && (
            <p className="py-12 text-center text-sm text-slate-400">
              Aucun message pour l&apos;instant. Posez une question ci-dessous.
            </p>
          )}

          {messages.map((msg, index) => (
            <div
              key={`${msg.role}-${index}`}
              className={`max-w-3xl rounded-lg px-4 py-3 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "ml-auto bg-brand-600 text-white"
                  : msg.error
                    ? "border border-red-200 bg-red-50 text-red-800"
                    : "border border-slate-100 bg-slate-50 text-slate-800"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.role === "assistant" && msg.sources?.length > 0 && (
                <ul className="mt-3 space-y-1 border-t border-slate-200/80 pt-2 text-xs text-slate-500">
                  <li className="font-semibold text-slate-600">Sources</li>
                  {msg.sources.map((src, i) => (
                    <li key={`${src.filename}-${i}`}>• {src.filename}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}

          {loading && (
            <p className="text-sm text-slate-400">Recherche en cours…</p>
          )}
        </div>

        <div className="border-t border-slate-200 p-4">
          <ChatBox onSubmit={handleAsk} disabled={loading} />
        </div>
      </div>
    </div>
  );
}
