function SectionCard({ title, children }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="bg-indigo-50 border-b border-indigo-100 px-6 py-3">
        <h2 className="text-indigo-800 font-semibold text-base">{title}</h2>
      </div>
      <div className="px-6 py-5 text-slate-700 text-sm leading-relaxed">{children}</div>
    </div>
  );
}

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

function JobDescriptionSection({ data }) {
  if (!data) return <p className="text-slate-400 italic">No data available.</p>;

  if (typeof data === 'string') return <p className="whitespace-pre-wrap">{data}</p>;

  return (
    <div className="space-y-4">
      {(data.role_level) && (
        <p className="text-xs font-medium text-indigo-600 uppercase tracking-wide">{data.role_level}</p>
      )}
      {data.summary && (
        <div>
          <h3 className="font-semibold text-slate-800 mb-1">Summary</h3>
          <p className="whitespace-pre-wrap">{data.summary}</p>
        </div>
      )}
      {data.responsibilities && (
        <div>
          <h3 className="font-semibold text-slate-800 mb-1">Responsibilities</h3>
          <BulletList items={data.responsibilities} />
        </div>
      )}
      {data.required_qualifications && (
        <div>
          <h3 className="font-semibold text-slate-800 mb-1">Required Qualifications</h3>
          <BulletList items={data.required_qualifications} />
        </div>
      )}
      {data.preferred_qualifications && (
        <div>
          <h3 className="font-semibold text-slate-800 mb-1">Preferred Qualifications</h3>
          <BulletList items={data.preferred_qualifications} />
        </div>
      )}
      {data.what_we_offer && (
        <div>
          <h3 className="font-semibold text-slate-800 mb-1">What We Offer</h3>
          <BulletList items={data.what_we_offer} />
        </div>
      )}
    </div>
  );
}

function ScorecardSection({ data }) {
  if (!data) return <p className="text-slate-400 italic">No data available.</p>;

  const items = Array.isArray(data) ? data : (data.dimensions || data.criteria || data.items || []);

  if (items.length === 0 && typeof data === 'string') {
    return <p className="whitespace-pre-wrap">{data}</p>;
  }

  return (
    <div className="space-y-3">
      {items.map((item, index) => (
        <div key={index} className="border-b border-slate-100 pb-3 last:border-0 last:pb-0">
          {typeof item === 'string' ? (
            <div className="flex gap-3 items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-700 text-xs font-bold rounded-full flex items-center justify-center mt-0.5">
                {index + 1}
              </span>
              <p>{item}</p>
            </div>
          ) : (
            <div className="flex gap-3 items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-700 text-xs font-bold rounded-full flex items-center justify-center mt-0.5">
                {index + 1}
              </span>
              <div className="flex-1">
                {(item.name || item.category) && (
                  <p className="font-semibold text-slate-800">{item.name || item.category}</p>
                )}
                {item.weight && <p className="text-xs text-indigo-600 mt-0.5">Weight: {item.weight}</p>}
                {item.criteria && item.criteria.length > 0 && (
                  <ul className="mt-1 list-disc list-inside space-y-0.5 text-slate-600">
                    {item.criteria.map((criterion, i) => (
                      <li key={i}>{criterion}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function QuestionList({ questions, label }) {
  if (!questions || questions.length === 0) return null;
  return (
    <div>
      <h3 className="font-semibold text-slate-700 text-sm uppercase tracking-wide mb-2">{label}</h3>
      <div className="space-y-4">
        {questions.map((item, index) => (
          <div key={index} className="space-y-1">
            <p className="font-semibold text-slate-800">
              {index + 1}. {typeof item === 'string' ? item : item.question}
            </p>
            {typeof item === 'object' && (item.what_to_listen_for || item.evaluation_criteria) && (
              <p className="text-slate-500 text-xs">
                <span className="font-medium">What to listen for: </span>
                {item.what_to_listen_for || item.evaluation_criteria}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function InterviewQuestionsSection({ data }) {
  if (!data) return <p className="text-slate-400 italic">No data available.</p>;

  if (Array.isArray(data)) {
    return (
      <div className="space-y-5">
        {data.map((item, index) => (
          <div key={index} className="space-y-1">
            <p className="font-semibold text-slate-800">
              {index + 1}. {typeof item === 'string' ? item : item.question}
            </p>
          </div>
        ))}
      </div>
    );
  }

  if (typeof data === 'string') return <p className="whitespace-pre-wrap">{data}</p>;

  return (
    <div className="space-y-6">
      <QuestionList questions={data.behavioral} label="Behavioral" />
      <QuestionList questions={data.technical} label="Technical" />
      <QuestionList questions={data.questions} label="Questions" />
    </div>
  );
}

function SkillsRubricSection({ data }) {
  if (!data) return <p className="text-slate-400 italic">No data available.</p>;

  const skills = Array.isArray(data) ? data : (data.skills || data.rubric || []);

  if (skills.length === 0 && typeof data === 'string') {
    return <p className="whitespace-pre-wrap">{data}</p>;
  }

  return (
    <div className="space-y-4">
      {skills.map((skill, index) => (
        <div key={index} className="border border-slate-200 rounded-lg overflow-hidden">
          {typeof skill === 'string' ? (
            <p className="px-4 py-3">{skill}</p>
          ) : (
            <>
              {skill.skill && (
                <div className="bg-slate-50 px-4 py-2 font-semibold text-slate-800 text-sm border-b border-slate-200">
                  {skill.skill}
                </div>
              )}
              <div className="px-4 py-3 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                {skill.levels ? (
                  [
                    ['below_expectations', 'Below Expectations'],
                    ['meets_expectations', 'Meets Expectations'],
                    ['exceeds_expectations', 'Exceeds Expectations'],
                  ].map(([key, label]) =>
                    skill.levels[key] ? (
                      <div key={key}>
                        <p className="font-semibold text-slate-600 mb-0.5">{label}</p>
                        <p className="text-slate-500">{skill.levels[key]}</p>
                      </div>
                    ) : null
                  )
                ) : (
                  ['beginner', 'intermediate', 'advanced'].map((level) =>
                    skill[level] ? (
                      <div key={level}>
                        <p className="font-semibold text-slate-600 capitalize mb-0.5">{level}</p>
                        <p className="text-slate-500">{skill[level]}</p>
                      </div>
                    ) : null
                  )
                )}
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  );
}

export default function KitDisplay({ kit }) {
  if (!kit) return null;

  const sections = kit.generated_kit || {};

  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col gap-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-slate-900">
          {kit.role_title || 'Interview Kit'}
        </h1>
        <p className="text-slate-500 text-sm mt-1">Your complete interview kit is ready.</p>
      </div>

      <SectionCard title="Job Description">
        <JobDescriptionSection data={sections.job_description} />
      </SectionCard>

      <SectionCard title="Interview Scorecard">
        <ScorecardSection data={sections.scorecard} />
      </SectionCard>

      <SectionCard title="Interview Questions">
        <InterviewQuestionsSection data={sections.interview_questions} />
      </SectionCard>

      <SectionCard title="Skills Assessment Rubric">
        <SkillsRubricSection data={sections.skills_assessment_rubric} />
      </SectionCard>
    </div>
  );
}
