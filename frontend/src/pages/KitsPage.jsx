import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import Navbar from '../components/Navbar';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { listKits, deleteKit } from '../api/kitApi';

function EmptyState() {
  return (
    <div className="text-center py-20">
      <div className="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mx-auto mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" />
        </svg>
      </div>
      <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-2">No kits yet</h2>
      <p className="text-slate-500 dark:text-slate-400 mb-6 max-w-xs mx-auto text-sm">
        Generate your first interview kit and it will appear here.
      </p>
      <Link
        to="/#form"
        onClick={() => setTimeout(() => document.getElementById('form')?.scrollIntoView({ behavior: 'smooth' }), 100)}
        className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-colors"
      >
        Generate your first kit
      </Link>
    </div>
  );
}

function KitCard({ kit, onDelete }) {
  const [isDeleting, setIsDeleting] = useState(false);

  async function handleDelete() {
    if (!window.confirm('Delete this kit? This cannot be undone.')) return;
    setIsDeleting(true);
    try {
      await deleteKit(kit.id);
      toast.success('Kit deleted');
      onDelete(kit.id);
    } catch {
      toast.error('Failed to delete kit');
      setIsDeleting(false);
    }
  }

  const date = new Date(kit.created_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 flex flex-col sm:flex-row sm:items-center gap-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-slate-900 dark:text-white truncate">{kit.role_title}</h3>
        <div className="flex flex-wrap items-center gap-2 mt-1.5">
          {kit.role_level && (
            <span className="text-xs bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 px-2 py-0.5 rounded-full font-medium border border-indigo-100 dark:border-indigo-800">
              {kit.role_level}
            </span>
          )}
          {kit.industry && (
            <span className="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-full font-medium">
              {kit.industry}
            </span>
          )}
          {kit.remote_policy && (
            <span className="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-full font-medium">
              {kit.remote_policy}
            </span>
          )}
          <span className="text-xs text-slate-400 dark:text-slate-500">{date}</span>
        </div>
      </div>
      <div className="flex items-center gap-2 flex-shrink-0">
        <Link
          to={`/kits/${kit.id}`}
          className="px-3 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 rounded-xl transition-colors"
        >
          View
        </Link>
        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="px-3 py-2 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-colors disabled:opacity-50"
        >
          {isDeleting ? 'Deleting…' : 'Delete'}
        </button>
      </div>
    </div>
  );
}

export default function KitsPage() {
  const [kits, setKits] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [nextPage, setNextPage] = useState(null);
  const [prevPage, setPrevPage] = useState(null);
  const [count, setCount] = useState(0);

  async function loadKits(url) {
    setIsLoading(true);
    try {
      const data = url
        ? await fetch(url).then((r) => r.json())
        : await listKits();
      setKits(data.results || []);
      setNextPage(data.next);
      setPrevPage(data.previous);
      setCount(data.count);
    } catch {
      setError('Failed to load kits. Is the backend running?');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadKits();
  }, []);

  function handleDelete(kitId) {
    setKits((prev) => prev.filter((k) => k.id !== kitId));
    setCount((prev) => prev - 1);
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Kit History</h1>
            {!isLoading && count > 0 && (
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                {count} kit{count !== 1 ? 's' : ''} generated
              </p>
            )}
          </div>
          <Link
            to="/"
            className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            New Kit
          </Link>
        </div>

        {isLoading && <LoadingSkeleton />}

        {error && !isLoading && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 text-red-700 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        {!isLoading && !error && kits.length === 0 && <EmptyState />}

        {!isLoading && kits.length > 0 && (
          <>
            <div className="flex flex-col gap-3">
              {kits.map((kit) => (
                <KitCard key={kit.id} kit={kit} onDelete={handleDelete} />
              ))}
            </div>

            {(prevPage || nextPage) && (
              <div className="flex justify-center gap-3 mt-8">
                <button
                  onClick={() => loadKits(prevPage)}
                  disabled={!prevPage}
                  className="px-4 py-2 text-sm font-medium border border-slate-200 dark:border-slate-700 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  Previous
                </button>
                <button
                  onClick={() => loadKits(nextPage)}
                  disabled={!nextPage}
                  className="px-4 py-2 text-sm font-medium border border-slate-200 dark:border-slate-700 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
