import { useState } from "react";
import api from "../services/api";

export default function UploadForm({ onResult }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || loading) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const { data } = await api.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onResult?.({ ok: true, data });
      setFile(null);
      e.target.reset();
    } catch (err) {
      onResult?.({
        ok: false,
        error: err.response?.data?.detail || err.message || "Échec de l'upload",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card-surface space-y-4 p-6">
      <div>
        <label htmlFor="file" className="mb-1 block text-sm font-medium text-slate-700">
          Fichier
        </label>
        <input
          id="file"
          type="file"
          className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-md file:border-0 file:bg-brand-50 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-brand-800 hover:file:bg-brand-100"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          required
        />
      </div>

      <button type="submit" className="btn-primary" disabled={!file || loading}>
        {loading ? "Envoi…" : "Téléverser"}
      </button>
    </form>
  );
}
