import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import Navbar from '../components/Navbar';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { useAuth } from '../context/AuthContext';
import { listKits, deleteKit, publishKit, logoutManager } from '../api/kitApi';

function StatusBadge({ status }) {
  const isPublished = status === 'published';
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
      isPublished
        ? 'bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 border border-green-100 dark:border-green-800'
        : 'bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 border border-amber-100 dark:border-amber-800'
    }`}>
      {isPublished ? 'Published' : 'Draft'}
    </span>
  );
}

function KitCard({ kit, onDelete, onTogglePublish }) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  const date = new Date(kit.created_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  });

  async function handleDelete() {
    if (!window.confirm('Delete this kit? This cannot be undone.')) return;
    setIsDeleting(true);
    try {
      await onDelete(kit.id);
    } finally {
      setIsDeleting(false);
    }
  }

  async function handleTogglePublish() {
    setIsToggling(true);
    try {
      await onTogglePublish(kit.id, kit.status === 'published' ? 'draft' : 'published');
    } finally {
      setIsToggling(false);
    }
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 flex flex-col sm:flex-row sm:items-center gap-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className="font-semibold text-slate-900 dark:text-white truncate">{kit.role_title}</h3>
          <StatusBadge status={kit.status} />
        </div>
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
          <span className="text-xs text-slate-400 dark:text-slate-500">{date}</span>
        </div>
      </div>
      <div className="flex items-center gap-2 flex-shrink-0 flex-wrap">
        <Link
          to={`/kits/${kit.id}`}
          className="px-3 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 rounded-xl transition-colors"
        >
          View
        </Link>
        <Link
          to={`/manager/roles/${kit.id}/edit`}
          className="px-3 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-colors"
        >
          Edit
        </Link>
        <button
          onClick={handleTogglePublish}
          disabled={isToggling}
          className="px-3 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-colors disabled:opacity-50"
        >
          {isToggling ? '…' : kit.status === 'published' ? 'Unpublish' : 'Publish'}
        </button>
        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="px-3 py-2 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-colors disabled:opacity-50"
        >
          {isDeleting ? '…' : 'Delete'}
        </button>
      </div>
    </div>
  );
}

export default function ManagerDashboard() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [kits, setKits] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchKits() {
      try {
        const data = await listKits(token);
        setKits(data.results || []);
      } catch {
        setError('Failed to load your kits. Try again later.');
      } finally {
        setIsLoading(false);
      }
    }
    fetchKits();
  }, [token]);

  async function handleDelete(kitId) {
    try {
      await deleteKit(token, kitId);
      setKits((prev) => prev.filter((k) => k.id !== kitId));
      toast.success('Kit deleted');
    } catch {
      toast.error('Failed to delete kit');
    }
  }

  async function handleTogglePublish(kitId, newStatus) {
    try {
      const updated = await publishKit(token, kitId, newStatus);
      setKits((prev) => prev.map((k) => (k.id === kitId ? updated : k)));
      toast.success(newStatus === 'published' ? 'Role published' : 'Role unpublished');
    } catch {
      toast.error('Failed to update status');
    }
  }

  async function handleLogout() {
    try {
      await logoutManager(token);
    } catch {
      // proceed with local logout even if server call fails
    }
    logout();
    navigate('/login');
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">My Roles</h1>
            {!isLoading && kits.length > 0 && (
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                {kits.length} role{kits.length !== 1 ? 's' : ''} total
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Link
              to="/manager/roles/new"
              className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              New Role
            </Link>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              Logout
            </button>
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
            <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-2">No roles yet</h2>
            <p className="text-slate-500 dark:text-slate-400 mb-6 max-w-xs mx-auto text-sm">
              Create your first role to generate an AI-powered interview kit.
            </p>
            <Link
              to="/manager/roles/new"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-colors"
            >
              Create your first role
            </Link>
          </div>
        )}

        {!isLoading && kits.length > 0 && (
          <div className="flex flex-col gap-3">
            {kits.map((kit) => (
              <KitCard
                key={kit.id}
                kit={kit}
                onDelete={handleDelete}
                onTogglePublish={handleTogglePublish}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
