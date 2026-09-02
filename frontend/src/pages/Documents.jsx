import { useEffect, useState } from "react";
import DocumentCard from "../components/DocumentCard";
import { deleteDocument, listDocuments } from "../services/documents";

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDocuments = async (cancelled = false) => {
    setLoading(true);
    setError("");
    try {
      const data = await listDocuments();
      if (!cancelled) setDocuments(data);
    } catch (err) {
      if (!cancelled) {
        setError(err.response?.data?.detail || "Impossible de charger les documents.");
      }
    } finally {
      if (!cancelled) setLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;
    loadDocuments(cancelled);

    return () => {
      cancelled = true;
    };
  }, []);

  const handleDelete = async (document) => {
    if (!window.confirm(`Supprimer le document "${document.title}" ?`)) return;
    try {
      await deleteDocument(document.id);
      await loadDocuments();
    } catch (err) {
      setError(err.response?.data?.detail || "Suppression impossible.");
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display text-2xl font-semibold text-slate-800">
          Documents
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Liste des documents enregistres dans la base.
        </p>
      </div>

      {loading && <p className="text-sm text-slate-400">Chargement...</p>}
      {error && (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      {!loading && !error && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {documents.map((doc) => (
            <DocumentCard key={doc.id} document={doc} onDelete={handleDelete} />
          ))}
          {documents.length === 0 && (
            <p className="text-sm text-slate-400">Aucun document.</p>
          )}
        </div>
      )}
    </div>
  );
}
