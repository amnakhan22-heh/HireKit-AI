export default function CVMatchResult({ result, onReset }) {
  const { compatibility_percentage, explanation, strengths_matched, gaps_identified } = result;

  const percentage = Math.min(100, Math.max(0, compatibility_percentage));
  const color =
    percentage >= 75 ? 'text-green-600 dark:text-green-400' :
    percentage >= 50 ? 'text-amber-600 dark:text-amber-400' :
    'text-red-600 dark:text-red-400';
  const barColor =
    percentage >= 75 ? 'bg-green-500' :
    percentage >= 50 ? 'bg-amber-500' :
    'bg-red-500';

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
        <h3 className="font-semibold text-slate-800 dark:text-slate-100 mb-4">CV Match Result</h3>

        <div className="flex items-center gap-4 mb-4">
          <span className={`text-5xl font-bold tabular-nums ${color}`}>
            {percentage}%
          </span>
          <div className="flex-1">
            <div className="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${barColor}`}
                style={{ width: `${percentage}%` }}
              />
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Compatibility Score</p>
          </div>
        </div>

        <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{explanation}</p>
      </div>

      {strengths_matched?.length > 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
          <h4 className="font-semibold text-slate-800 dark:text-slate-100 mb-3">Strengths Matched</h4>
          <ul className="space-y-2">
            {strengths_matched.map((strength, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300">
                <span className="mt-0.5 flex-shrink-0 w-5 h-5 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 flex items-center justify-center text-xs font-bold">✓</span>
                {strength}
              </li>
            ))}
          </ul>
        </div>
      )}

      {gaps_identified?.length > 0 && (
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
          <h4 className="font-semibold text-slate-800 dark:text-slate-100 mb-3">Gaps Identified</h4>
          <ul className="space-y-2">
            {gaps_identified.map((gap, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300">
                <span className="mt-0.5 flex-shrink-0 w-5 h-5 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 flex items-center justify-center text-xs font-bold">!</span>
                {gap}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="text-center">
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
