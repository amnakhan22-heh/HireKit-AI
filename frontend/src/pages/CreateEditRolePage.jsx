import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import RoleForm from '../components/RoleForm';
import KitDisplay from '../components/KitDisplay';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { useAuth } from '../context/AuthContext';
import { generateFullKit, getKit, updateKit } from '../api/kitApi';

export default function CreateEditRolePage() {
  const { id } = useParams();
  const isEditMode = Boolean(id);
  const { token } = useAuth();
  const navigate = useNavigate();

  const [existingKit, setExistingKit] = useState(null);
  const [isLoadingKit, setIsLoadingKit] = useState(isEditMode);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generatedKit, setGeneratedKit] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (!isEditMode) return;
    async function fetchKit() {
      try {
        const data = await getKit(id);
        setExistingKit(data);
      } catch {
        setErrorMessage('Failed to load kit data.');
      } finally {
        setIsLoadingKit(false);
      }
    }
    fetchKit();
  }, [id, isEditMode]);

  async function handleSubmit(formData) {
    setIsSubmitting(true);
    setErrorMessage('');
    setGeneratedKit(null);
    try {
      if (isEditMode) {
        const updated = await updateKit(token, id, {
          role_description: formData.roleDescription,
          role_title: formData.roleTitle,
        });
        setGeneratedKit(updated);
      } else {
        const kit = await generateFullKit(token, formData);
        setGeneratedKit(kit);
      }
    } catch (error) {
      setErrorMessage(error.message || 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoadingKit) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
        <Navbar />
        <main className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
          <LoadingSkeleton />
        </main>
      </div>
    );
  }

  const prefillData = existingKit ? {
    roleDescription: existingKit.role_description,
    roleLevel: existingKit.role_level,
    industry: existingKit.industry,
    companySize: existingKit.company_size,
    remotePolicy: existingKit.remote_policy,
  } : null;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
        <div className="mb-6">
          <Link
            to="/manager"
            className="inline-flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Back to Dashboard
          </Link>
        </div>

        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            {isEditMode ? 'Edit Role' : 'Create New Role'}
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto">
            {isEditMode
              ? 'Update the role details below.'
              : 'Describe your role and we\'ll generate a complete interview kit.'}
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
          <RoleForm onSubmit={handleSubmit} isLoading={isSubmitting} prefillData={prefillData} />
        </div>

        {errorMessage && (
          <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl px-5 py-4">
            <p className="text-red-700 dark:text-red-400 text-sm font-medium">Error</p>
            <p className="text-red-600 dark:text-red-400 text-sm mt-0.5">{errorMessage}</p>
          </div>
        )}

        {isSubmitting && (
          <div className="mt-6">
            <LoadingSkeleton />
          </div>
        )}

        {generatedKit && !isSubmitting && (
          <div className="mt-8">
            <KitDisplay kit={generatedKit} />
            <div className="text-center mt-6">
              <button
                onClick={() => navigate('/manager')}
                className="px-5 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
