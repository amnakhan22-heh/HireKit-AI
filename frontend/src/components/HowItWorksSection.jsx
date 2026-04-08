const STEPS = [
  {
    number: '01',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
      </svg>
    ),
    title: 'Describe the role',
    description: 'Tell us about the position in plain language — level, industry, team size, and what you need. No templates required.',
  },
  {
    number: '02',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3" /><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" />
      </svg>
    ),
    title: 'AI generates your kit',
    description: 'AI generates an inclusive job description, interview scorecard, behavioral & technical questions, and a skills rubric tailored to your context.',
  },
  {
    number: '03',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" />
      </svg>
    ),
    title: 'Export, share, or refine',
    description: 'Download as PDF, share a link with your team, copy individual sections, regenerate any part, or edit inline — all in one click.',
  },
];

export default function HowItWorksSection() {
  return (
    <section className="py-16 bg-white dark:bg-slate-900 border-y border-slate-100 dark:border-slate-800">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-3">
            For Hiring Managers
          </h2>
          <p className="text-slate-500 dark:text-slate-400 max-w-lg mx-auto">
            From role description to complete interview kit in under a minute.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
          {STEPS.map((step, index) => (
            <div key={step.number} className="relative flex flex-col items-center text-center">
              {index < STEPS.length - 1 && (
                <div className="hidden sm:block absolute top-7 left-[calc(50%+2rem)] right-0 h-px bg-gradient-to-r from-indigo-200 to-transparent dark:from-indigo-800" />
              )}
              <div className="relative z-10 w-14 h-14 rounded-2xl bg-indigo-50 dark:bg-indigo-900/40 border border-indigo-100 dark:border-indigo-800 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4">
                {step.icon}
                <span className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-indigo-600 text-white text-[10px] font-bold flex items-center justify-center">
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
