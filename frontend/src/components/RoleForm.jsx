import { useState } from 'react';

export default function RoleForm({ onSubmit, isLoading }) {
  const [roleTitle, setRoleTitle] = useState('');
  const [roleDescription, setRoleDescription] = useState('');
  const [validationError, setValidationError] = useState('');

  function handleSubmit(event) {
    event.preventDefault();
    setValidationError('');

    if (!roleTitle.trim()) {
      setValidationError('Role title is required.');
      return;
    }
    if (!roleDescription.trim()) {
      setValidationError('Role description is required.');
      return;
    }

    onSubmit(roleTitle.trim(), roleDescription.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto flex flex-col gap-5">
      <div className="flex flex-col gap-1.5">
        <label htmlFor="role_title" className="text-sm font-medium text-slate-700">
          Role Title
        </label>
        <input
          id="role_title"
          type="text"
          value={roleTitle}
          onChange={(e) => setRoleTitle(e.target.value)}
          placeholder="e.g. Senior Backend Engineer"
          disabled={isLoading}
          className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="role_description" className="text-sm font-medium text-slate-700">
          Role Description
        </label>
        <textarea
          id="role_description"
          value={roleDescription}
          onChange={(e) => setRoleDescription(e.target.value)}
          placeholder="Describe the role in plain language — team context, key responsibilities, must-have skills, and the kind of person who would thrive here."
          rows={6}
          disabled={isLoading}
          className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50 resize-vertical"
        />
      </div>

      {validationError && (
        <p className="text-sm text-red-600">{validationError}</p>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="self-end px-6 py-2.5 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'Generating…' : 'Generate Interview Kit'}
      </button>
    </form>
  );
}
