const STEPS = [
  {
    number: '01',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
    ),
    title: 'Browse open roles',
    description: 'Explore published job postings to find roles that match your background, skills, and experience level.',
  },
  {
    number: '02',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
      </svg>
    ),
    title: 'Upload your CV',
    description: 'Submit your resume as a PDF directly on the role page — no account or sign-up required.',
  },
  {
    number: '03',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
    title: 'Get your match score',
    description: 'Receive an instant AI-powered breakdown of how well your profile fits the role, including strengths and gaps.',
  },
];

export default function CVHowItWorksSection() {
  return (
    <section className="py-16 bg-slate-50 dark:bg-slate-950 border-t border-slate-100 dark:border-slate-800">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-3">
            For Candidates
          </h2>
          <p className="text-slate-500 dark:text-slate-400 max-w-lg mx-auto">
            See how your CV stacks up against a role in seconds — no account needed.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
          {STEPS.map((step, index) => (
            <div key={step.number} className="relative flex flex-col items-center text-center">
              {index < STEPS.length - 1 && (
                <div className="hidden sm:block absolute top-7 left-[calc(50%+2rem)] right-0 h-px bg-gradient-to-r from-violet-200 to-transparent dark:from-violet-800" />
              )}
              <div className="relative z-10 w-14 h-14 rounded-2xl bg-violet-50 dark:bg-violet-900/40 border border-violet-100 dark:border-violet-800 flex items-center justify-center text-violet-600 dark:text-violet-400 mb-4">
                {step.icon}
                <span className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-violet-600 text-white text-[10px] font-bold flex items-center justify-center">
                  {index + 1}
                </span>
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white mb-2">{step.title}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
