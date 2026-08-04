import { useState } from "react";

export default function ChatBox({ onSubmit, disabled }) {
  const [question, setQuestion] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || disabled) return;
    setQuestion("");
    await onSubmit(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        className="input-field flex-1"
        placeholder="Posez votre question…"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        disabled={disabled}
        aria-label="Question"
      />
      <button type="submit" className="btn-primary shrink-0" disabled={disabled || !question.trim()}>
        Envoyer
      </button>
    </form>
  );
}
