import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import KitDisplay from '../components/KitDisplay';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { useAuth } from '../context/AuthContext';
import { getKit } from '../api/kitApi';

export default function KitDetailPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const [kit, setKit] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchKit() {
      try {
        const data = await getKit(id, token);
        setKit(data);
      } catch {
        setError('Kit not found or could not be loaded.');
      } finally {
        setIsLoading(false);
      }
    }
    fetchKit();
  }, [id, token]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
        <div className="mb-6">
          <Link
            to={token ? '/manager' : '/kits'}
            className="inline-flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            {token ? 'Back to My Roles' : 'Back to Open Roles'}
          </Link>
        </div>

        {isLoading && <LoadingSkeleton />}

        {error && !isLoading && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-5">
            <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
            <Link to={token ? '/manager' : '/kits'} className="text-sm text-red-600 dark:text-red-400 underline mt-2 inline-block">
              {token ? 'Back to My Roles' : 'Back to Open Roles'}
            </Link>
          </div>
        )}

        {!isLoading && kit && (
          <KitDisplay kit={kit} />
        )}
      </main>
    </div>
  );
}
