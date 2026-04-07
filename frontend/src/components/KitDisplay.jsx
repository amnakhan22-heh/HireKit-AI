import { useState } from 'react';
import toast from 'react-hot-toast';
import KitSection from './KitSection';

function BulletList({ items }) {
  if (!items || items.length === 0) return null;
  return (
    <ul className="list-disc list-inside space-y-1">
      {items.map((item, index) => (
        <li key={index}>{typeof item === 'object' ? JSON.stringify(item) : item}</li>
      ))}
    </ul>
  );
}

function JobDescriptionContent({ data }) {
  if (!data) return <p className="text-slate-400 italic">No data available.</p>;
  if (typeof data === 'string') return <p className="whitespace-pre-wrap">{data}</p>;
  return (
    <div className="space-y-4 text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
      {data.role_level && (
        <p className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wide">
          {data.role_level}
        </p>
      )}
      {data.summary && (
        <div>
          <h4 className="font-semibold text-slate-800 dark:text-slate-100 mb-1">Summary</h4>
          <p>{data.summary}</p>
        </div>
      )}
      {data.responsibilities?.length > 0 && (
        <div>
          <h4 className="font-semibold text-slate-800 dark:text-slate-100 mb-1">Responsibilities</h4>
          <BulletList items={data.responsibilities} />
        </div>
      )}
      {data.required_qualifications?.length > 0 && (
        <div>
          <h4 className="font-semibold text-slate-800 dark:text-slate-100 mb-1">Required Qualifications</h4>
          <BulletList items={data.required_qualifications} />
        </div>
      )}
      {data.preferred_qualifications?.length > 0 && (
        <div>
          <h4 className="font-semibold text-slate-800 dark:text-slate-100 mb-1">Preferred Qualifications</h4>
          <BulletList items={data.preferred_qualifications} />
        </div>
      )}
      {data.what_we_offer?.length > 0 && (
        <div>
          <h4 className="font-semibold text-slate-800 dark:text-slate-100 mb-1">What We Offer</h4>
          <BulletList items={data.what_we_offer} />
        </div>
      )}
    </div>
  );
}

function ScorecardContent({ data }) {
  if (!data) return <p className="text-slate-400 italic">No data available.</p>;
  const dimensions = Array.isArray(data) ? data : (data.dimensions || []);
  return (
    <div className="space-y-3">
      {dimensions.map((dim, index) => (
        <div key={index} className="border border-slate-100 dark:border-slate-700 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <p className="font-semibold text-slate-800 dark:text-slate-100 text-sm">{dim.name}</p>
            {dim.weight && (
              <span className="text-xs font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 px-2 py-0.5 rounded-full">
                {dim.weight}
              </span>
            )}
          </div>
          {dim.criteria?.length > 0 && (
            <ul className="list-disc list-inside text-sm text-slate-600 dark:text-slate-400 space-y-0.5">
              {dim.criteria.map((c, i) => <li key={i}>{c}</li>)}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
}

function QuestionGroup({ questions, label }) {
  if (!questions?.length) return null;
  return (
    <div>
      <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">{label}</h4>
      <div className="space-y-4">
        {questions.map((item, index) => (
          <div key={index} className="border-l-2 border-indigo-100 dark:border-indigo-800 pl-4">
            <p className="font-medium text-slate-800 dark:text-slate-100 text-sm">
              {index + 1}. {typeof item === 'string' ? item : item.question}
            </p>
            {typeof item === 'object' && item.what_to_listen_for && (
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                <span className="font-semibold">Listen for: </span>
                {item.what_to_listen_for}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function InterviewQuestionsContent({ data }) {
  if (!data) return <p className="text-slate-400 italic">No data available.</p>;
  if (typeof data === 'string') return <p className="whitespace-pre-wrap text-sm">{data}</p>;
  return (
    <div className="space-y-6">
      <QuestionGroup questions={data.behavioral} label="Behavioral" />
      <QuestionGroup questions={data.technical} label="Technical" />
    </div>
  );
}

function SkillsRubricContent({ data }) {
  if (!data) return <p className="text-slate-400 italic">No data available.</p>;
  const skills = Array.isArray(data) ? data : (data.skills || []);
  return (
    <div className="space-y-4">
      {skills.map((skill, index) => (
        <div key={index} className="border border-slate-100 dark:border-slate-700 rounded-xl overflow-hidden">
          <div className="bg-slate-50 dark:bg-slate-700/50 px-4 py-2 border-b border-slate-100 dark:border-slate-700">
            <p className="font-semibold text-slate-800 dark:text-slate-100 text-sm">{skill.skill}</p>
          </div>
          {skill.levels && (
            <div className="grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-slate-100 dark:divide-slate-700">
              {[
                ['below_expectations', 'Below', 'text-red-600 dark:text-red-400'],
                ['meets_expectations', 'Meets', 'text-amber-600 dark:text-amber-400'],
                ['exceeds_expectations', 'Exceeds', 'text-green-600 dark:text-green-400'],
              ].map(([key, label, colorClass]) => (
                <div key={key} className="px-4 py-3 text-xs">
                  <p className={`font-semibold mb-1 ${colorClass}`}>{label}</p>
                  <p className="text-slate-500 dark:text-slate-400 leading-relaxed">{skill.levels[key]}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

const SECTION_CONFIG = [
  {
    key: 'job_description',
    title: 'Job Description',
    ContentComponent: JobDescriptionContent,
  },
  {
    key: 'scorecard',
    title: 'Interview Scorecard',
    ContentComponent: ScorecardContent,
  },
  {
    key: 'interview_questions',
    title: 'Interview Questions',
    ContentComponent: InterviewQuestionsContent,
  },
  {
    key: 'skills_assessment_rubric',
    title: 'Skills Assessment Rubric',
    ContentComponent: SkillsRubricContent,
  },
];

export default function KitDisplay({ kit, onSectionRegenerated }) {
  const [sections, setSections] = useState(kit?.generated_kit || {});

  function handleSectionRegenerated(sectionName, newData) {
    setSections((prev) => ({ ...prev, [sectionName]: newData }));
    if (onSectionRegenerated) onSectionRegenerated(sectionName, newData);
  }

  function handleExportPdf() {
    import('../utils/exportPdf').then(({ exportKitAsPdf }) => {
      exportKitAsPdf('kit-display');
    });
  }

  async function handleShare() {
    const url = kit?.id ? `${window.location.origin}/kits/${kit.id}` : window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      toast.success('Link copied to clipboard');
    } catch {
      toast.error('Failed to copy link');
    }
  }

  if (!kit) return null;

  const printDate = new Date().toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  });

  return (
    <div className="w-full">
      {/* Print-only header — hidden on screen, shown in PDF */}
      <div
        id="print-header"
        style={{ display: 'none' }}
        aria-hidden="true"
      >
        <span>{printDate}</span>
        <span>HireKit AI</span>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {kit.role_title || 'Interview Kit'}
          </h2>
          <div className="flex flex-wrap gap-2 mt-1.5">
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
            {kit.company_size && (
              <span className="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-full font-medium">
                {kit.company_size}
              </span>
            )}
            {kit.remote_policy && (
              <span className="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-full font-medium">
                {kit.remote_policy}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={handleShare}
            className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" /><polyline points="16 6 12 2 8 6" /><line x1="12" y1="2" x2="12" y2="15" />
            </svg>
            Share
          </button>
          <button
            onClick={handleExportPdf}
            className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Export PDF
          </button>
        </div>
      </div>

      <div id="kit-display" className="flex flex-col gap-4">
        {SECTION_CONFIG.map(({ key, title, ContentComponent }) => (
          <KitSection
            key={key}
            title={title}
            sectionName={key}
            sectionData={sections[key]}
            kitId={kit.id}
            onRegenerated={handleSectionRegenerated}
          >
            <div className="p-5">
              <ContentComponent data={sections[key]} />
            </div>
          </KitSection>
        ))}
      </div>
    </div>
  );
}
