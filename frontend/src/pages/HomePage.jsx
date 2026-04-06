import { useState } from 'react';
import RoleForm from '../components/RoleForm';
import KitDisplay from '../components/KitDisplay';
import LoadingSpinner from '../components/LoadingSpinner';
import { generateFullKit } from '../api/kitApi';

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [generatedKit, setGeneratedKit] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  async function handleFormSubmit(roleTitle, roleDescription) {
    setIsLoading(true);
    setErrorMessage('');
    setGeneratedKit(null);

    try {
      const kit = await generateFullKit(roleTitle, roleDescription);
      setGeneratedKit(kit);
    } catch (error) {
      setErrorMessage(error.message || 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  function handleReset() {
    setGeneratedKit(null);
    setErrorMessage('');
  }

  return (
    <main className="min-h-screen bg-slate-50 py-12 px-4">
      <div className="max-w-3xl mx-auto flex flex-col gap-10">
        <header className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-slate-900">Interview Kit Generator</h1>
          <p className="text-slate-500 max-w-lg mx-auto">
            Describe a role in plain language and get a polished, inclusive job description,
            scorecard, interview questions, and skills rubric — instantly.
          </p>
        </header>

        {!generatedKit && (
          <RoleForm onSubmit={handleFormSubmit} isLoading={isLoading} />
        )}

        {isLoading && <LoadingSpinner />}

        {errorMessage && (
          <div className="w-full max-w-2xl mx-auto bg-red-50 border border-red-200 rounded-lg px-5 py-4">
            <p className="text-red-700 text-sm font-medium">Error</p>
            <p className="text-red-600 text-sm mt-0.5">{errorMessage}</p>
          </div>
        )}

        {generatedKit && !isLoading && (
          <>
            <KitDisplay kit={generatedKit} />
            <div className="text-center">
              <button
                onClick={handleReset}
                className="px-5 py-2 text-sm font-medium text-indigo-600 border border-indigo-300 rounded-lg hover:bg-indigo-50 transition-colors"
              >
                Generate Another Kit
              </button>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
