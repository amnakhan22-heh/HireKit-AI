import { useState } from 'react';
import toast from 'react-hot-toast';
import { regenerateSection } from '../api/kitApi';
import { useAuth } from '../context/AuthContext';

function CopyIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

function RefreshIcon({ spinning }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={spinning ? 'animate-spin' : ''}>
      <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" /><path d="M21 3v5h-5" /><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" /><path d="M8 16H3v5" />
    </svg>
  );
}

function EditIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" /><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  );
}

function sectionToText(sectionData) {
  return JSON.stringify(sectionData, null, 2);
}

export default function KitSection({ title, sectionName, sectionData, kitId, onRegenerated, children }) {
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState('');
  const { token } = useAuth();

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(sectionToText(sectionData));
      toast.success('Section copied to clipboard');
    } catch {
      toast.error('Failed to copy to clipboard');
    }
  }

  async function handleRegenerate() {
    if (!kitId) {
      toast.error('No kit ID — cannot regenerate');
      return;
    }
    setIsRegenerating(true);
    try {
      const result = await regenerateSection(token, kitId, sectionName);
      onRegenerated(sectionName, result.data);
      toast.success('Section regenerated successfully');
    } catch (error) {
      toast.error(error.message || 'Regeneration failed');
    } finally {
      setIsRegenerating(false);
    }
  }

  function handleEdit() {
    setEditValue(sectionToText(sectionData));
    setIsEditing(true);
  }

  function handleSaveEdit() {
    try {
      const parsed = JSON.parse(editValue);
      onRegenerated(sectionName, parsed);
      setIsEditing(false);
      toast.success('Section updated');
    } catch {
      toast.error('Invalid JSON — please fix before saving');
    }
  }

  function handleCancelEdit() {
    setIsEditing(false);
    setEditValue('');
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm">
      <div className="flex items-center justify-between px-5 py-3 bg-slate-50 dark:bg-slate-700/50 border-b border-slate-200 dark:border-slate-700">
        <h3 className="font-semibold text-slate-800 dark:text-slate-100 text-sm">{title}</h3>
        {!isEditing && (
          <div className="flex items-center gap-1.5">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-lg transition-colors"
              title="Copy section"
            >
              <CopyIcon /> Copy
            </button>
            {kitId && token && (
              <button
                onClick={handleRegenerate}
                disabled={isRegenerating}
                className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Regenerate this section"
              >
                <RefreshIcon spinning={isRegenerating} />
                {isRegenerating ? 'Regenerating…' : 'Regenerate'}
              </button>
            )}
            <button
              onClick={handleEdit}
              className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-lg transition-colors"
              title="Edit section"
            >
              <EditIcon /> Edit
            </button>
          </div>
        )}
        {isEditing && (
          <div className="flex items-center gap-2">
            <button
              onClick={handleCancelEdit}
              className="px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveEdit}
              className="px-3 py-1.5 text-xs font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors"
            >
              Save
            </button>
          </div>
        )}
      </div>

      {isEditing ? (
        <div className="p-4">
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">
            Edit the JSON directly. Click Save when done.
          </p>
          <textarea
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            rows={16}
            className="w-full font-mono text-xs bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg p-3 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-y"
            spellCheck={false}
          />
        </div>
      ) : (
        <div className="relative">
          {isRegenerating && (
            <div className="absolute inset-0 bg-white/70 dark:bg-slate-800/70 z-10 flex items-center justify-center rounded-b-2xl">
              <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                <svg className="animate-spin w-4 h-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Generating a fresh version…
              </div>
            </div>
          )}
          {children}
        </div>
      )}
    </div>
  );
}
