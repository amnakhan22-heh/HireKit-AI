import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { listKits } from '../api/kitApi';

function RoleCard({ kit }) {
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
          to={`/roles/${kit.id}`}
          className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-colors"
        >
          View &amp; Apply
        </Link>
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
      setError('Failed to load open roles. Try again later.');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadKits();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Open Roles</h1>
            {!isLoading && count > 0 && (
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                {count} open role{count !== 1 ? 's' : ''} available
              </p>
            )}
          </div>
        </div>

        {isLoading && <LoadingSkeleton />}

        {error && !isLoading && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 text-red-700 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        {!isLoading && !error && kits.length === 0 && (
          <div className="text-center py-20">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-2">No open roles</h2>
            <p className="text-slate-500 dark:text-slate-400 max-w-xs mx-auto text-sm">
              Check back soon for new opportunities.
            </p>
          </div>
        )}

        {!isLoading && kits.length > 0 && (
          <>
            <div className="flex flex-col gap-3">
              {kits.map((kit) => (
                <RoleCard key={kit.id} kit={kit} />
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
