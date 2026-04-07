function SkeletonBlock({ className }) {
  return (
    <div className={`bg-slate-200 dark:bg-slate-700 rounded animate-pulse ${className}`} />
  );
}

function SectionSkeleton() {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div className="h-12 bg-slate-100 dark:bg-slate-700/60 px-5 flex items-center justify-between">
        <SkeletonBlock className="h-4 w-32" />
        <div className="flex gap-2">
          <SkeletonBlock className="h-7 w-16 rounded-lg" />
          <SkeletonBlock className="h-7 w-20 rounded-lg" />
        </div>
      </div>
      <div className="p-5 space-y-3">
        <SkeletonBlock className="h-4 w-full" />
        <SkeletonBlock className="h-4 w-5/6" />
        <SkeletonBlock className="h-4 w-4/6" />
        <div className="pt-2 space-y-2">
          <SkeletonBlock className="h-3 w-full" />
          <SkeletonBlock className="h-3 w-11/12" />
          <SkeletonBlock className="h-3 w-10/12" />
          <SkeletonBlock className="h-3 w-9/12" />
        </div>
      </div>
    </div>
  );
}

export default function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-6">
        <div className="h-6 w-6 rounded-full bg-indigo-200 dark:bg-indigo-800 animate-pulse" />
        <SkeletonBlock className="h-5 w-48" />
      </div>
      {[1, 2, 3, 4].map((i) => (
        <SectionSkeleton key={i} />
      ))}
    </div>
  );
}
