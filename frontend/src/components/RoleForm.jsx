import { useState } from 'react';

const ROLE_LEVELS = ['Junior', 'Mid-level', 'Senior', 'Lead'];
const INDUSTRIES = ['Tech', 'Finance', 'Healthcare', 'Marketing', 'Operations', 'Other'];
const COMPANY_SIZES = ['Startup', 'Mid-size', 'Enterprise'];
const REMOTE_POLICIES = ['Remote', 'Hybrid', 'On-site'];

function SelectField({ id, label, hint, value, onChange, options, disabled }) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium text-slate-700 dark:text-slate-300">
        {label}
      </label>
      {hint && <p className="text-xs text-slate-400 dark:text-slate-500">{hint}</p>}
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50 cursor-pointer"
      >
        <option value="">Select…</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
    </div>
  );
}

export default function RoleForm({ onSubmit, isLoading }) {
  const [roleTitle, setRoleTitle] = useState('');
  const [roleDescription, setRoleDescription] = useState('');
  const [roleLevel, setRoleLevel] = useState('');
  const [industry, setIndustry] = useState('');
  const [companySize, setCompanySize] = useState('');
  const [remotePolicy, setRemotePolicy] = useState('');
  const [validationError, setValidationError] = useState('');

  function handleSubmit(event) {
    event.preventDefault();
    setValidationError('');

    if (!roleTitle.trim()) {
      setValidationError('Role title is required.');
      return;
    }
    if (!roleDescription.trim() || roleDescription.trim().length < 20) {
      setValidationError('Role description must be at least 20 characters.');
      return;
    }

    onSubmit({
      roleTitle: roleTitle.trim(),
      roleDescription: roleDescription.trim(),
      roleLevel,
      industry,
      companySize,
      remotePolicy,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="w-full flex flex-col gap-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <div className="sm:col-span-2 flex flex-col gap-1">
          <label htmlFor="role_title" className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Role Title
          </label>
          <p className="text-xs text-slate-400 dark:text-slate-500">
            The position name — the AI will standardize it to industry norms
          </p>
          <input
            id="role_title"
            type="text"
            value={roleTitle}
            onChange={(e) => setRoleTitle(e.target.value)}
            placeholder="e.g. Senior Backend Engineer"
            disabled={isLoading}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50"
          />
        </div>

        <SelectField
          id="role_level"
          label="Role Level"
          hint="Adjusts seniority expectations in the kit"
          value={roleLevel}
          onChange={setRoleLevel}
          options={ROLE_LEVELS}
          disabled={isLoading}
        />

        <SelectField
          id="industry"
          label="Industry"
          hint="Tailors terminology and domain-specific content"
          value={industry}
          onChange={setIndustry}
          options={INDUSTRIES}
          disabled={isLoading}
        />

        <SelectField
          id="company_size"
          label="Company Size"
          hint="Shapes culture language and scope of role"
          value={companySize}
          onChange={setCompanySize}
          options={COMPANY_SIZES}
          disabled={isLoading}
        />

        <SelectField
          id="remote_policy"
          label="Remote Policy"
          hint="Included in responsibilities and benefits"
          value={remotePolicy}
          onChange={setRemotePolicy}
          options={REMOTE_POLICIES}
          disabled={isLoading}
        />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="role_description" className="text-sm font-medium text-slate-700 dark:text-slate-300">
          Role Description
        </label>
        <p className="text-xs text-slate-400 dark:text-slate-500">
          Describe the role in plain language — team context, key responsibilities, must-have skills, and ideal candidate traits
        </p>
        <textarea
          id="role_description"
          value={roleDescription}
          onChange={(e) => setRoleDescription(e.target.value.slice(0, 3000))}
          placeholder="e.g. We're a Series B fintech startup looking for a senior backend engineer to lead our payments API. They'll own architecture decisions, mentor 2 junior engineers, and collaborate closely with product. Must have 5+ years of experience with Python and distributed systems."
          rows={6}
          disabled={isLoading}
          className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50 resize-vertical"
        />
        <p className={`text-xs text-right ${roleDescription.length >= 3000 ? 'text-red-500' : 'text-slate-400 dark:text-slate-500'}`}>
          {roleDescription.length} / 3000 characters
        </p>
      </div>

      {validationError && (
        <p className="text-sm text-red-600 dark:text-red-400">{validationError}</p>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="self-start px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl shadow-md shadow-indigo-200 dark:shadow-indigo-900/50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:-translate-y-0.5 active:translate-y-0"
      >
        {isLoading ? 'Generating…' : 'Generate Interview Kit'}
      </button>
    </form>
  );
}
