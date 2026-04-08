import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import HowItWorksSection from '../components/HowItWorksSection';
import CVHowItWorksSection from '../components/CVHowItWorksSection';
import { useAuth } from '../context/AuthContext';

export default function HowItWorksPage() {
  const { token } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 pt-12 pb-4 text-center">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white mb-3">
          How It Works
        </h1>
        <p className="text-slate-500 dark:text-slate-400 max-w-xl mx-auto">
          Whether you're hiring or applying, here's how HireKit AI fits into your workflow.
        </p>
      </div>

      <HowItWorksSection />
      <CVHowItWorksSection />

      <section className="py-14">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 text-center">
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              to="/kits"
              className="px-6 py-3 bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold rounded-xl transition-colors"
            >
              Browse Open Roles
            </Link>
            {token ? (
              <Link
                to="/manager"
                className="px-6 py-3 text-sm font-semibold text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Go to My Roles
              </Link>
            ) : (
              <Link
                to="/login"
                className="px-6 py-3 text-sm font-semibold text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Login as Manager
              </Link>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
