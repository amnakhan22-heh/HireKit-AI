import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import HowItWorksSection from '../components/HowItWorksSection';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />
      <HeroSection />
      <HowItWorksSection />

      <section className="py-14">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 text-center">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
            Get Started
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto mb-8">
            Applicants can browse open roles, or managers can log in to create and manage interview kits.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              to="/kits"
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-colors"
            >
              Browse Open Roles
            </Link>
            <Link
              to="/login"
              className="px-6 py-3 text-sm font-semibold text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              Manager Login
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
