export default function DocumentCard({ document, onDelete }) {
  return (
    <article className="card-surface p-4 transition hover:border-brand-200">
      <div className="flex items-start justify-between gap-3">
        <h3 className="min-w-0 font-display text-base font-semibold text-slate-800">
          {document.title}
        </h3>
        {document.can_delete && onDelete && (
          <button type="button" className="btn-secondary min-h-8 px-3 py-1 text-xs" onClick={() => onDelete(document)}>
            Supprimer
          </button>
        )}
      </div>
      <dl className="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-500">
        <div>
          <dt className="font-medium text-slate-400">ID</dt>
          <dd className="mt-0.5 text-slate-700">{document.id}</dd>
        </div>
      </dl>
    </article>
  );
}
