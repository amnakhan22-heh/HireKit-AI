const RECOMMENDATION_CONFIG = {
  'Strong Fit':   { bg: 'bg-green-500',  light: 'bg-green-50 dark:bg-green-900/20',   border: 'border-green-200 dark:border-green-800',   text: 'text-green-700 dark:text-green-300',   badge: 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300' },
  'Good Fit':     { bg: 'bg-blue-500',   light: 'bg-blue-50 dark:bg-blue-900/20',     border: 'border-blue-200 dark:border-blue-800',     text: 'text-blue-700 dark:text-blue-300',     badge: 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300' },
  'Possible Fit': { bg: 'bg-amber-500',  light: 'bg-amber-50 dark:bg-amber-900/20',   border: 'border-amber-200 dark:border-amber-800',   text: 'text-amber-700 dark:text-amber-300',   badge: 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300' },
  'Not a Fit':    { bg: 'bg-red-500',    light: 'bg-red-50 dark:bg-red-900/20',       border: 'border-red-200 dark:border-red-800',       text: 'text-red-700 dark:text-red-300',       badge: 'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300' },
};

const MATCH_LEVEL_CONFIG = {
  'Strong Match':  'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300',
  'Good Match':    'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
  'Partial Match': 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300',
};

const CRITICALITY_CONFIG = {
  'Critical':  'bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300',
  'Important': 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300',
  'Minor':     'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300',
};

function ScoreRing({ percentage, color }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;
  return (
    <div className="relative flex items-center justify-center w-36 h-36">
      <svg className="absolute inset-0 -rotate-90" width="144" height="144" viewBox="0 0 144 144">
        <circle cx="72" cy="72" r={radius} fill="none" stroke="currentColor" strokeWidth="10" className="text-slate-100 dark:text-slate-700" />
        <circle
          cx="72" cy="72" r={radius} fill="none" strokeWidth="10"
          stroke="currentColor" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          className={`transition-all duration-700 ${color}`}
        />
      </svg>
      <span className={`text-3xl font-bold tabular-nums ${color}`}>{percentage}%</span>
    </div>
  );
}

function SectionCard({ title, icon, children, className = '' }) {
  return (
    <div className={`bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm ${className}`}>
      <h4 className="flex items-center gap-2 font-semibold text-slate-800 dark:text-slate-100 mb-4">
        <span className="text-lg">{icon}</span>
        {title}
      </h4>
      {children}
    </div>
  );
}

export default function CVMatchResult({ result, onReset }) {
  const {
    compatibility_percentage,
    score_explanation,
    executive_summary,
    key_strengths = [],
    key_gaps = [],
    experience_analysis,
    cultural_and_role_fit,
    recommendation,
    recommendation_detail,
  } = result;

  const percentage = Math.min(100, Math.max(0, compatibility_percentage));

  const scoreColor =
    percentage >= 75 ? 'text-green-500' :
    percentage >= 50 ? 'text-amber-500' :
    'text-red-500';

  const barColor =
    percentage >= 75 ? 'bg-green-500' :
    percentage >= 50 ? 'bg-amber-500' :
    'bg-red-500';

  const rec = RECOMMENDATION_CONFIG[recommendation] ?? RECOMMENDATION_CONFIG['Possible Fit'];

  return (
    <div className="space-y-5">

      {/* Score Header */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
          <ScoreRing percentage={percentage} color={scoreColor} />
          <div className="flex-1 text-center sm:text-left">
            <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-3">
              <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Compatibility Score</h3>
              {recommendation && (
                <span className={`inline-block self-center px-3 py-1 rounded-full text-xs font-semibold ${rec.badge}`}>
                  {recommendation}
                </span>
              )}
            </div>
            <div className="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-2 mb-3">
              <div className={`h-2 rounded-full transition-all duration-700 ${barColor}`} style={{ width: `${percentage}%` }} />
            </div>
            {score_explanation && (
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{score_explanation}</p>
            )}
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      {executive_summary && (
        <SectionCard title="Executive Summary" icon="📋">
          <div className="space-y-3">
            {executive_summary.split('\n').filter(Boolean).map((para, i) => (
              <p key={i} className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{para}</p>
            ))}
          </div>
        </SectionCard>
      )}

      {/* Strengths + Gaps side by side on wide screens */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

        {/* Key Strengths */}
        {key_strengths.length > 0 && (
          <SectionCard title={`Key Strengths (${key_strengths.length})`} icon="✅">
            <ul className="space-y-4">
              {key_strengths.map((item, i) => (
                <li key={i} className="border-b border-slate-100 dark:border-slate-700 last:border-0 pb-4 last:pb-0">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <span className="text-sm font-medium text-slate-800 dark:text-slate-100">{item.strength}</span>
                    <span className={`flex-shrink-0 text-xs font-semibold px-2 py-0.5 rounded-full ${MATCH_LEVEL_CONFIG[item.match_level] ?? MATCH_LEVEL_CONFIG['Partial Match']}`}>
                      {item.match_level}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{item.relevance}</p>
                </li>
              ))}
            </ul>
          </SectionCard>
        )}

        {/* Key Gaps */}
        {key_gaps.length > 0 && (
          <SectionCard title={`Key Gaps (${key_gaps.length})`} icon="⚠️">
            <ul className="space-y-4">
              {key_gaps.map((item, i) => (
                <li key={i} className="border-b border-slate-100 dark:border-slate-700 last:border-0 pb-4 last:pb-0">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <span className="text-sm font-medium text-slate-800 dark:text-slate-100">{item.gap}</span>
                    <span className={`flex-shrink-0 text-xs font-semibold px-2 py-0.5 rounded-full ${CRITICALITY_CONFIG[item.criticality] ?? CRITICALITY_CONFIG['Minor']}`}>
                      {item.criticality}
                    </span>
                  </div>
                  <span className={`inline-block text-xs px-2 py-0.5 rounded-full mt-1 ${
                    item.learnable_on_job
                      ? 'bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400'
                      : 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400'
                  }`}>
                    {item.learnable_on_job ? 'Can learn on the job' : 'Requires prior experience'}
                  </span>
                </li>
              ))}
            </ul>
          </SectionCard>
        )}
      </div>

      {/* Experience Analysis */}
      {experience_analysis && (
        <SectionCard title="Experience Analysis" icon="📊">
          <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{experience_analysis}</p>
        </SectionCard>
      )}

      {/* Cultural & Role Fit */}
      {cultural_and_role_fit && (
        <SectionCard title="Cultural & Role Fit" icon="🏢">
          <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{cultural_and_role_fit}</p>
        </SectionCard>
      )}

      {/* Recommendation */}
      {recommendation && (
        <div className={`rounded-2xl border p-6 ${rec.light} ${rec.border}`}>
          <div className="flex items-center gap-3 mb-3">
            <h4 className="font-semibold text-slate-800 dark:text-slate-100">Hiring Recommendation</h4>
            <span className={`px-3 py-1 rounded-full text-sm font-bold ${rec.badge}`}>{recommendation}</span>
          </div>
          {recommendation_detail && (
            <p className={`text-sm leading-relaxed ${rec.text}`}>{recommendation_detail}</p>
          )}
        </div>
      )}

      {/* Reset */}
      <div className="text-center pt-2">
        <button
          onClick={onReset}
          className="px-5 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          Try with a different CV
        </button>
      </div>
    </div>
  );
}
