import { useState } from "react";
import UploadForm from "../components/UploadForm";

export default function Upload() {
  const [result, setResult] = useState(null);

  return (
    <div className="max-w-xl">
      <div className="mb-6">
        <h1 className="font-display text-2xl font-semibold text-slate-800">
          Upload de document
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Envoi multipart vers POST /documents/upload (indexation RAG côté serveur).
        </p>
      </div>

      <UploadForm onResult={setResult} />

      {result?.ok && (
        <div
          className={`mt-4 rounded-md border px-4 py-3 text-sm ${
            result.data.status === "uploaded_and_indexed"
              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
              : "border-amber-200 bg-amber-50 text-amber-900"
          }`}
        >
          <p className="font-semibold">{result.data.filename}</p>
          <p className="mt-1">Statut : {result.data.status}</p>
          {result.data.error && (
            <p className="mt-2 text-xs opacity-90">{result.data.error}</p>
          )}
        </div>
      )}

      {result && !result.ok && (
        <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {result.error}
        </p>
      )}
    </div>
  );
}
