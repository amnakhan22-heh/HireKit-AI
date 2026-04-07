import { useState, useRef } from 'react';
import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import HowItWorksSection from '../components/HowItWorksSection';
import RoleForm from '../components/RoleForm';
import KitDisplay from '../components/KitDisplay';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { generateFullKit } from '../api/kitApi';

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [generatedKit, setGeneratedKit] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const kitSectionRef = useRef(null);

  async function handleFormSubmit(formData) {
    setIsLoading(true);
    setErrorMessage('');
    setGeneratedKit(null);

    try {
      const kit = await generateFullKit(formData);
      setGeneratedKit(kit);
      setTimeout(() => {
        kitSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (error) {
      setErrorMessage(error.message || 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  function handleReset() {
    setGeneratedKit(null);
    setErrorMessage('');
    setTimeout(() => {
      document.getElementById('form')?.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />
      <HeroSection />
      <HowItWorksSection />

      <section id="form" className="py-14">
        <div className="max-w-3xl mx-auto px-4 sm:px-6">
          <div className="mb-8 text-center">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
              Describe your role
            </h2>
            <p className="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto">
              The more context you provide, the more tailored and useful your kit will be.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
            <RoleForm onSubmit={handleFormSubmit} isLoading={isLoading} />
          </div>

          {errorMessage && (
            <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl px-5 py-4">
              <p className="text-red-700 dark:text-red-400 text-sm font-medium">Error</p>
              <p className="text-red-600 dark:text-red-400 text-sm mt-0.5">{errorMessage}</p>
            </div>
          )}
        </div>
      </section>

      {(isLoading || generatedKit) && (
        <section
          id="kit"
          ref={kitSectionRef}
          className="py-10 border-t border-slate-100 dark:border-slate-800"
        >
          <div className="max-w-3xl mx-auto px-4 sm:px-6">
            {isLoading && <LoadingSkeleton />}

            {generatedKit && !isLoading && (
              <div className="animate-fade-in">
                <KitDisplay kit={generatedKit} />
                <div className="text-center mt-8">
                  <button
                    onClick={handleReset}
                    className="px-5 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                  >
                    Generate Another Kit
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
