import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import LoadingSkeleton from '../components/LoadingSkeleton';
import CVMatchResult from '../components/CVMatchResult';
import { getKit, matchCv } from '../api/kitApi';

export default function RoleDetailPage() {
  const { id } = useParams();
  const [kit, setKit] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [cvFile, setCvFile] = useState(null);
  const [isMatching, setIsMatching] = useState(false);
  const [matchResult, setMatchResult] = useState(null);
  const [matchError, setMatchError] = useState('');

  useEffect(() => {
    async function fetchKit() {
      try {
        const data = await getKit(id);
        setKit(data);
      } catch {
        setError('Role not found or is no longer available.');
      } finally {
        setIsLoading(false);
      }
    }
    fetchKit();
  }, [id]);

  async function handleCvSubmit(e) {
    e.preventDefault();
    if (!cvFile) return;
    setIsMatching(true);
    setMatchResult(null);
    setMatchError('');
    try {
      const result = await matchCv(id, cvFile);
      setMatchResult(result);
    } catch (err) {
      setMatchError(err.message || 'CV analysis failed. Please try again.');
    } finally {
      setIsMatching(false);
    }
  }

  function handleReset() {
    setCvFile(null);
    setMatchResult(null);
    setMatchError('');
  }

  const jobDescription = kit?.generated_kit?.job_description;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
        <div className="mb-6">
          <Link
            to="/kits"
            className="inline-flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Browse Roles
          </Link>
        </div>

        {isLoading && <LoadingSkeleton />}

        {error && !isLoading && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-5">
            <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
          </div>
        )}

        {!isLoading && kit && (
          <>
            <div className="mb-2">
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{kit.role_title}</h1>
              <div className="flex flex-wrap gap-2 mt-2">
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
              </div>
            </div>

            {jobDescription && (
              <div className="mt-6 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm space-y-4 text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                {jobDescription.summary && <p>{jobDescription.summary}</p>}
                {jobDescription.responsibilities?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-slate-800 dark:text-slate-100 mb-2">Responsibilities</h3>
                    <ul className="list-disc list-inside space-y-1">
                      {jobDescription.responsibilities.map((r, i) => <li key={i}>{r}</li>)}
                    </ul>
                  </div>
                )}
                {jobDescription.required_qualifications?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-slate-800 dark:text-slate-100 mb-2">Required Qualifications</h3>
                    <ul className="list-disc list-inside space-y-1">
                      {jobDescription.required_qualifications.map((q, i) => <li key={i}>{q}</li>)}
                    </ul>
                  </div>
                )}
                {jobDescription.preferred_qualifications?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-slate-800 dark:text-slate-100 mb-2">Preferred Qualifications</h3>
                    <ul className="list-disc list-inside space-y-1">
                      {jobDescription.preferred_qualifications.map((q, i) => <li key={i}>{q}</li>)}
                    </ul>
                  </div>
                )}
                {jobDescription.what_we_offer?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-slate-800 dark:text-slate-100 mb-2">What We Offer</h3>
                    <ul className="list-disc list-inside space-y-1">
                      {jobDescription.what_we_offer.map((o, i) => <li key={i}>{o}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <div className="mt-10">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Check Your Fit</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
                Upload your CV (PDF) and our AI will analyze how well you match this role.
              </p>

              {!matchResult ? (
                <form onSubmit={handleCvSubmit} className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Upload your CV
                  </label>
                  <input
                    type="file"
                    accept="application/pdf"
                    onChange={(e) => { setCvFile(e.target.files[0] || null); setMatchResult(null); }}
                    className="block w-full text-sm text-slate-500 dark:text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 dark:file:bg-indigo-900/30 dark:file:text-indigo-300"
                  />
                  {cvFile && (
                    <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{cvFile.name}</p>
                  )}
                  {matchError && (
                    <p className="mt-2 text-sm text-red-600 dark:text-red-400">{matchError}</p>
                  )}
                  <button
                    type="submit"
                    disabled={!cvFile || isMatching}
                    className="mt-4 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-colors disabled:opacity-60"
                  >
                    {isMatching ? 'Analyzing…' : 'Analyze My CV'}
                  </button>
                </form>
              ) : (
                <CVMatchResult result={matchResult} onReset={handleReset} />
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
