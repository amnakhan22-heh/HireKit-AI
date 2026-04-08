import { Link } from 'react-router-dom';

export default function HeroSection({ viewKitsTo = '/kits', getStartedTo = '/login' }) {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-indigo-50 via-white to-slate-50 dark:from-slate-900 dark:via-slate-900 dark:to-indigo-950 py-20 sm:py-28">
      <div className="absolute inset-0 opacity-30 dark:opacity-10" aria-hidden="true">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-200 dark:bg-indigo-800 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-violet-200 dark:bg-violet-900 rounded-full blur-3xl translate-y-1/2 -translate-x-1/4" />
      </div>

      <div className="relative max-w-5xl mx-auto px-4 sm:px-6 text-center">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 dark:text-white leading-tight tracking-tight mb-5">
          Generate polished{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600 dark:from-indigo-400 dark:to-violet-400">
            interview kits
          </span>{' '}
          in seconds
        </h1>

        <p className="text-lg sm:text-xl text-slate-500 dark:text-slate-400 max-w-2xl mx-auto mb-8 leading-relaxed">
          Describe a role in plain language and receive a complete, inclusive job description,
          scorecard, behavioral questions, and skills rubric — ready to use immediately.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            to={getStartedTo}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl shadow-lg shadow-indigo-200 dark:shadow-indigo-900/50 transition-all hover:-translate-y-0.5 active:translate-y-0"
          >
            Get Started
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="m6 9 6 6 6-6" />
            </svg>
          </Link>
          <Link
            to={viewKitsTo}
            className="inline-flex items-center justify-center px-6 py-3 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-semibold rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            View Kits
          </Link>
        </div>
      </div>
    </section>
  );
}
