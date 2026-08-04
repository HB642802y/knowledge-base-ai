export default function DocumentCard({ document }) {
  return (
    <article className="card-surface p-4 transition hover:border-brand-200">
      <h3 className="font-display text-base font-semibold text-slate-800">
        {document.title}
      </h3>
      <dl className="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-500">
        <div>
          <dt className="font-medium text-slate-400">ID</dt>
          <dd className="mt-0.5 text-slate-700">{document.id}</dd>
        </div>
        <div>
          <dt className="font-medium text-slate-400">Source</dt>
          <dd className="mt-0.5 text-slate-700">{document.source}</dd>
        </div>
      </dl>
    </article>
  );
}
