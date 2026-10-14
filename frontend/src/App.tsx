import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';

type Status = 'MATCH' | 'MISMATCH' | 'MISSING_INFORMATION';

type Opportunity = {
  id: number;
  title: string;
  organization: string;
  category: string;
  description: string;
  location?: string;
  remote?: string;
  deadline?: string;
  application_url?: string;
  source_url?: string;
  requirements?: Array<Record<string, any>>;
  verification_status?: string;
  last_checked?: string;
};

type Profile = {
  name: string;
  email: string;
  college: string;
  degree: string;
  department: string;
  current_year: string;
  graduation_year: number | null;
  marks?: number | null;
  cgpa: number | string | null;
  annual_income?: number | null;
  team_size?: number | null;
  skills: string[];
  projects?: string[];
  resume_url: string;
  github_url: string;
  linkedin_url: string;
  documents: Record<string, string | boolean>;
};

type Application = {
  id: number;
  opportunity_id: number;
  status: string;
  application_date?: string | null;
  notes?: string | null;
  reminder_date?: string | null;
};

type EligibilityFit = 'Eligible' | 'Needs information' | 'Not eligible';

type ResumeData = {
  fullName: string;
  email: string;
  phone: string;
  location: string;
  headline: string;
  summary: string;
  education: string;
  skills: string;
  projects: string;
  experience: string;
  certifications: string;
  links: string;
};

const resumeFields: Array<keyof ResumeData> = [
  'fullName', 'email', 'phone', 'location', 'headline', 'summary',
  'education', 'skills', 'projects', 'experience', 'certifications', 'links',
];

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

type NavKey = 'dashboard' | 'explore' | 'analyze' | 'checklist' | 'tracker' | 'resume' | 'profile';

const API_BASE = 'http://localhost:8001';
const RESUME_STORAGE_KEY = 'opportunitykit-resume';

const emptyResume: ResumeData = {
  fullName: '',
  email: '',
  phone: '',
  location: '',
  headline: '',
  summary: '',
  education: '',
  skills: '',
  projects: '',
  experience: '',
  certifications: '',
  links: '',
};

const navItems: Array<{ key: NavKey; label: string; icon: string }> = [
  { key: 'dashboard', label: 'Overview', icon: '◫' },
  { key: 'explore', label: 'Explore Opportunities', icon: '⌕' },
  { key: 'analyze', label: 'Analyze Opportunity', icon: '◎' },
  { key: 'checklist', label: 'My Checklist', icon: '✓' },
  { key: 'tracker', label: 'Application Tracker', icon: '▣' },
  { key: 'resume', label: 'Resume Builder', icon: '▤' },
  { key: 'profile', label: 'My Profile', icon: '◌' },
];

function App() {
  const [tab, setTab] = useState<NavKey>('dashboard');
  const [profile, setProfile] = useState<Profile | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [eligibilityByOpportunity, setEligibilityByOpportunity] = useState<Record<number, EligibilityFit>>({});
  const [selectedOpportunityId, setSelectedOpportunityId] = useState<number | null>(null);
  const [checklistOpportunityId, setChecklistOpportunityId] = useState<number | null>(null);
  const [analysis, setAnalysis] = useState<any | null>(null);
  const [extractedRequirements, setExtractedRequirements] = useState<any[]>([]);
  const [manualText, setManualText] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [eligibilityFilter, setEligibilityFilter] = useState('All');
  const [eligibilityRefresh, setEligibilityRefresh] = useState(0);
  const [resume, setResume] = useState<ResumeData>(emptyResume);
  const [resumeLoaded, setResumeLoaded] = useState(false);
  const [resumeStorageReady, setResumeStorageReady] = useState(false);
  const [resumeWasStored, setResumeWasStored] = useState(false);
  const [resumeSaveError, setResumeSaveError] = useState('');
  const [applicationMessage, setApplicationMessage] = useState('');
  const [newOpportunity, setNewOpportunity] = useState({
    title: 'Sample Technical Fellowship',
    organization: 'Northstar Foundation',
    category: 'fellowship',
    description: 'CGPA 7.5+, Python and SQL required, resume and transcript needed. Preferred if graduation year is 2028 or later.',
    location: 'Remote',
    remote: 'Remote',
    deadline: '2026-11-25',
    application_url: 'https://example.com/fellowship',
  });

  useEffect(() => {
    Promise.all([
      axios.get(`${API_BASE}/api/profile`),
      axios.get(`${API_BASE}/api/opportunities`),
      axios.get(`${API_BASE}/api/applications`),
    ]).then(([profileRes, oppRes, applicationsRes]) => {
      setProfile(profileRes.data);
      setOpportunities(oppRes.data);
      setApplications(applicationsRes.data);
      if (oppRes.data.length > 0) {
        setSelectedOpportunityId(oppRes.data[0].id);
        setChecklistOpportunityId(oppRes.data[0].id);
      }
    }).catch(() => {
      setApplications([]);
      setProfile({
        name: 'Roshini S.',
        email: 'roshini@example.com',
        college: 'VIT Vellore',
        degree: 'B.Tech',
        department: 'Computer Science',
        current_year: '3rd Year',
        graduation_year: 2027,
        marks: null,
        cgpa: 8.2,
        annual_income: null,
        team_size: null,
        skills: ['Python', 'SQL', 'React', 'JavaScript', 'FastAPI'],
        projects: ['AI resume matcher', 'Smart campus portal'],
        resume_url: 'https://example.com/resume',
        github_url: 'https://github.com/roshini',
        linkedin_url: 'https://linkedin.com/in/roshini',
        documents: { resume: 'uploaded', transcript: 'uploaded' },
      });
      setOpportunities([
        {
          id: 1,
          title: 'Python Development Internship',
          organization: 'Nova Labs',
          category: 'Internship',
          description: 'Work on Python-based backend tooling and data pipelines for a product analytics team.',
          location: 'Bengaluru',
          remote: 'Hybrid',
          deadline: '2026-11-15',
          application_url: 'https://example.com/opportunity/1',
          verification_status: 'Verified',
          requirements: [
            { name: 'CGPA', expected_value: 'Minimum 7.0', status: 'mandatory' },
            { name: 'Python', expected_value: 'Python experience', status: 'mandatory' },
            { name: 'Resume', expected_value: 'Resume uploaded', status: 'mandatory' },
            { name: 'SQL', expected_value: 'SQL preferred', status: 'preferred' },
          ],
        },
        {
          id: 2,
          title: 'Women in STEM Scholarship',
          organization: 'Future Foundry',
          category: 'Scholarship',
          description: 'Support for women in engineering and applied sciences with academic and income-based criteria.',
          location: 'Remote',
          remote: 'Remote',
          deadline: '2026-10-30',
          application_url: 'https://example.com/scholarship',
          verification_status: 'Unverified',
          requirements: [
            { name: 'CGPA', expected_value: 'Minimum 8.0', status: 'mandatory' },
            { name: 'Income certificate', expected_value: 'Required', status: 'mandatory' },
            { name: 'Department', expected_value: 'CS or ECE preferred', status: 'preferred' },
          ],
        },
        {
          id: 3,
          title: 'Graduate Software Engineer',
          organization: 'Orbit Systems',
          category: 'Job',
          description: 'Build and maintain web services with JavaScript or Python. Open to 2027 graduates with a CGPA of 7.0 or higher.',
          location: 'Chennai',
          remote: 'Hybrid',
          deadline: '2026-12-10',
          application_url: 'https://example.com/jobs/graduate-engineer',
          verification_status: 'Unverified',
          requirements: [
            { name: 'CGPA', expected_value: 'Minimum 7.0', status: 'mandatory', required: true, comparison_type: 'cgpa_min', value: 7.0 },
            { name: 'Graduation year', expected_value: '2027 or later', status: 'mandatory', required: true, comparison_type: 'graduation_year_min', value: 2027 },
            { name: 'Python', expected_value: 'Python experience', status: 'mandatory', required: true, comparison_type: 'skill', value: 'python' },
          ],
        },
      ]);
      setSelectedOpportunityId(1);
      setChecklistOpportunityId(1);
    });
  }, []);

  useEffect(() => {
    if (!resumeLoaded || resumeWasStored || !profile || resume.fullName || resume.email) return;
    setResume((current) => ({
      ...current,
      fullName: profile.name,
      email: profile.email,
      location: '',
      education: [profile.degree, profile.department, profile.college, profile.graduation_year ? `Expected graduation: ${profile.graduation_year}` : ''].filter(Boolean).join(' · '),
      skills: profile.skills.join(', '),
      projects: profile.projects?.join('\n') ?? '',
      links: [profile.github_url, profile.linkedin_url].filter(Boolean).join('\n'),
    }));
  }, [resumeLoaded, resumeWasStored, profile, resume.fullName, resume.email]);

  useEffect(() => {
    let storedResume: string | null = null;
    try {
      storedResume = window.localStorage.getItem(RESUME_STORAGE_KEY);
      if (storedResume) {
        const parsedResume: unknown = JSON.parse(storedResume);
        if (isRecord(parsedResume)) {
          setResumeWasStored(true);
          const restored = { ...emptyResume };
          for (const field of resumeFields) {
            if (typeof parsedResume[field] === 'string') restored[field] = parsedResume[field];
          }
          setResume(restored);
          setResumeStorageReady(true);
        } else {
          setResumeSaveError('Saved resume data is invalid. Please update and save your resume again.');
        }
      } else {
        setResumeStorageReady(true);
      }
    } catch {
      setResumeSaveError('Could not read the saved resume from this browser.');
    } finally {
      setResumeLoaded(true);
    }
  }, []);

  useEffect(() => {
    if (!resumeLoaded || !resumeStorageReady) return;
    try {
      window.localStorage.setItem(RESUME_STORAGE_KEY, JSON.stringify(resume));
      setResumeSaveError('');
    } catch {
      setResumeSaveError('Resume changes could not be saved in this browser. Check available storage and try again.');
    }
  }, [resume, resumeLoaded, resumeStorageReady]);

  useEffect(() => {
    if (!opportunities.length) {
      setEligibilityByOpportunity({});
      return;
    }
    let cancelled = false;
    Promise.all(opportunities.map(async (opportunity) => {
      try {
        const response = await axios.post(`${API_BASE}/api/opportunities/${opportunity.id}/analyze`);
        const summary = response.data.summary;
        const fit: EligibilityFit = summary.mandatory_mismatches.length > 0
          ? 'Not eligible'
          : summary.missing > 0
            ? 'Needs information'
            : 'Eligible';
        return [opportunity.id, fit] as const;
      } catch {
        return null;
      }
    })).then((results) => {
      if (!cancelled) {
        setEligibilityByOpportunity(Object.fromEntries(results.filter((result): result is NonNullable<typeof result> => result !== null)));
      }
    });
    return () => {
      cancelled = true;
    };
  }, [opportunities, eligibilityRefresh]);

  useEffect(() => {
    if (!selectedOpportunityId) return;
    axios.post(`${API_BASE}/api/opportunities/${selectedOpportunityId}/analyze`).then((res) => setAnalysis(res.data)).catch(() => {
      setAnalysis({
        summary: { match: 5, mismatch: 0, missing: 1, mandatory_mismatches: [] },
        results: [
          { name: 'CGPA', evaluation_status: 'MATCH', explanation: 'Your CGPA meets the requirement.', recommended_action: 'No action needed.' },
          { name: 'Graduation year', evaluation_status: 'MATCH', explanation: 'Your graduation year fits the timeline.', recommended_action: 'No action needed.' },
          { name: 'Python', evaluation_status: 'MISSING_INFORMATION', explanation: 'Python experience is not yet confirmed in your profile.', recommended_action: 'Add a project or self-assessment.' },
        ],
      });
    });
  }, [selectedOpportunityId]);

  const filteredOpportunities = useMemo(() => {
    const normalizedQuery = searchQuery.trim().toLowerCase();

    return opportunities.filter((opportunity) => {
      const normalizedCategory = opportunity.category.toLowerCase();
      const matchesCategory = selectedCategory === 'All'
        || (selectedCategory === 'Job' ? normalizedCategory.includes('job') || normalizedCategory.includes('employment') : normalizedCategory.includes(selectedCategory.toLowerCase()));
      const matchesEligibility = eligibilityFilter === 'All' || eligibilityByOpportunity[opportunity.id] === eligibilityFilter;
      const haystack = [
        opportunity.title,
        opportunity.organization,
        opportunity.category,
        opportunity.description,
        opportunity.location,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

      const matchesQuery = !normalizedQuery || haystack.includes(normalizedQuery);
      return matchesCategory && matchesQuery && matchesEligibility;
    });
  }, [opportunities, searchQuery, selectedCategory, eligibilityFilter, eligibilityByOpportunity]);

  const selectedOpportunity = useMemo(
    () => filteredOpportunities.find((item) => item.id === selectedOpportunityId) ?? filteredOpportunities[0],
    [filteredOpportunities, selectedOpportunityId],
  );
  const checklistOpportunity = opportunities.find((item) => item.id === checklistOpportunityId) ?? opportunities[0];
  const checklistAnalysis = analysis?.opportunity_id === checklistOpportunity?.id ? analysis : null;
  const checklistResults: Array<Record<string, any>> = checklistAnalysis?.results ?? [];
  const checklistStatusCounts = checklistResults.reduce(
    (counts, item) => {
      if (item.evaluation_status === 'MATCH') counts.match += 1;
      else if (item.evaluation_status === 'MISMATCH') counts.mismatch += 1;
      else counts.missing += 1;
      return counts;
    },
    { match: 0, mismatch: 0, missing: 0 },
  );

  useEffect(() => {
    if (!filteredOpportunities.length) return;
    if (!selectedOpportunityId || !filteredOpportunities.some((opportunity) => opportunity.id === selectedOpportunityId)) {
      setSelectedOpportunityId(filteredOpportunities[0].id);
    }
  }, [filteredOpportunities, selectedOpportunityId]);

  const handleProfileChange = (
    field: keyof Profile,
    value: string | number | string[] | Record<string, string | boolean> | null,
  ) => {
    setProfile((current) => (current ? { ...current, [field]: value } : null));
  };

  const saveProfile = async () => {
    if (!profile) return;
    try {
      await axios.put(`${API_BASE}/api/profile`, profile);
      setEligibilityRefresh((value) => value + 1);
      alert('Profile updated successfully.');
    } catch {
      alert('Profile could not be saved. Check that the API is running and try again.');
    }
  };

  const extractFromText = async () => {
    const sourceText = manualText || newOpportunity.description;
    const response = await axios.post(`${API_BASE}/api/opportunities/extract`, { text: sourceText });
    setExtractedRequirements(response.data.requirements);
  };

  const addOpportunity = async () => {
    await axios.post(`${API_BASE}/api/opportunities`, {
      ...newOpportunity,
      requirements: extractedRequirements.length ? extractedRequirements : [
        { name: 'CGPA', category: 'academics', required: true, status: 'mandatory', expected_value: 'Minimum 7.0', comparison_type: 'cgpa_min', value: 7.0 },
      ],
    });
    const oppRes = await axios.get(`${API_BASE}/api/opportunities`);
    setOpportunities(oppRes.data);
    setTab('explore');
    alert('Opportunity added successfully.');
  };

  const trackOpportunity = async (opportunity: Opportunity) => {
    if (applications.some((application) => application.opportunity_id === opportunity.id)) {
      setApplicationMessage('This opportunity is already in your application tracker.');
      return;
    }
    try {
      const response = await axios.post(`${API_BASE}/api/applications`, {
        opportunity_id: opportunity.id,
        status: 'saved',
      });
      setApplications((current) => [response.data.application, ...current]);
      setApplicationMessage(`${opportunity.title} was added to your tracker.`);
    } catch {
      setApplicationMessage('Could not add this opportunity to your tracker. Check that the API is running and try again.');
    }
  };

  const updateApplicationStatus = async (application: Application, status: string) => {
    try {
      const response = await axios.patch(`${API_BASE}/api/applications/${application.id}`, {
        opportunity_id: application.opportunity_id,
        status,
      });
      setApplications((current) => current.map((item) => item.id === application.id ? response.data.application : item));
    } catch {
      setApplicationMessage('Application status could not be updated. Please try again.');
    }
  };

  const updateResume = (field: keyof ResumeData, value: string) => {
    setResumeStorageReady(true);
    setResume((current) => ({ ...current, [field]: value }));
  };

  const resumeLines = (value: string) => value.split('\n').map((line) => line.trim()).filter(Boolean);

  const statusClass = (status: Status) => {
    if (status === 'MATCH') return 'match';
    if (status === 'MISMATCH') return 'mismatch';
    return 'missing';
  };
  const statusLabel = (status: Status) => status === 'MATCH' ? 'Match' : status === 'MISMATCH' ? 'Mismatch' : 'Missing information';

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-wrap">
          <div className="brand-mark">O</div>
          <div>
            <div className="eyebrow">Student intelligence</div>
            <h1>OPPORTUNITYKIT</h1>
          </div>
        </div>

        <nav className="nav">
          {navItems.map((item) => (
            <button
              key={item.key}
              onClick={() => setTab(item.key)}
              className={`nav-item ${tab === item.key ? 'active' : ''}`}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="profile-mini">
          <div className="avatar">{(profile?.name ?? 'RS').split(/\s+/).map((part) => part[0]).slice(0, 2).join('').toUpperCase()}</div>
          <div>
            <strong>{profile?.name ?? 'Roshini S.'}</strong>
            <span>{profile?.current_year ?? '3rd Year'}</span>
          </div>
        </div>
      </aside>

      <main className="content-area">
        <header className="topbar">
          <div>
            <div className="eyebrow">Opportunity readiness</div>
            <h2>{tab === 'dashboard' ? 'Overview' : tab === 'explore' ? 'Explore Opportunities' : tab === 'analyze' ? 'Analyze Opportunity' : tab === 'checklist' ? 'My Checklist' : tab === 'tracker' ? 'Application Tracker' : tab === 'resume' ? 'Resume Builder' : 'My Profile'}</h2>
          </div>

          <div className="topbar-actions">
            <input
              aria-label="Search opportunities"
              className="search-box"
              placeholder="Search opportunities"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
            />
            <button className="ghost-button">🔔</button>
            <button className="primary-button" onClick={() => setTab('analyze')}>Analyze an Opportunity</button>
          </div>
        </header>

        {tab === 'dashboard' && (
          <div className="space-y-6">
            <section className="hero-panel">
              <div>
                <div className="eyebrow muted">Good evening, {profile?.name.split(' ')[0] ?? 'there'}</div>
                <h3>Your next opportunity starts with knowing where you stand.</h3>
                <p>Discover internships, scholarships, and competitions. Understand the requirements before you apply.</p>
                <div className="hero-actions">
                  <button className="primary-button" onClick={() => setTab('analyze')}>Analyze an Opportunity</button>
                  <button className="secondary-button" onClick={() => setTab('explore')}>Explore Opportunities</button>
                </div>
              </div>

              <div className="mini-report">
                <div className="mini-header">
                  <span className="mini-label">Opportunity fit</span>
                  <span className="status-pill match">MATCH</span>
                </div>
                <div className="mini-body">
                  <div className="score-block">
                    <strong>82%</strong>
                    <span>Profile fit</span>
                  </div>
                  <ul>
                    <li>CGPA requirement satisfied</li>
                    <li>Python skill needs confirmation</li>
                    <li>Resume ready for submission</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="grid four-col">
              {[
                { label: 'Opportunities that match', value: '12', tone: 'violet' },
                { label: 'Saved opportunities', value: '7', tone: 'soft' },
                { label: 'Upcoming deadlines', value: '4', tone: 'amber' },
                { label: 'Applications in progress', value: '3', tone: 'green' },
              ].map((card) => (
                <div key={card.label} className={`stat-card ${card.tone}`}>
                  <span>{card.label}</span>
                  <strong>{card.value}</strong>
                </div>
              ))}
            </section>

            <section className="grid two-col">
              <div className="panel">
                <div className="panel-header">
                  <h4>Recommended for you</h4>
                  <button className="text-button" onClick={() => setTab('explore')}>View all</button>
                </div>

                <div className="card-list">
                  {opportunities.map((opportunity) => (
                    <button
                      key={opportunity.id}
                      className="list-card"
                      onClick={() => {
                        setSelectedOpportunityId(opportunity.id);
                        setTab('explore');
                      }}
                    >
                      <div className="list-card-head">
                        <div>
                          <strong>{opportunity.title}</strong>
                          <span>{opportunity.organization}</span>
                        </div>
                        <span className="tag">{opportunity.category}</span>
                      </div>
                      <p>{opportunity.description}</p>
                      <div className="meta-row">
                        <span>{opportunity.deadline ?? 'TBD'}</span>
                        <span>{opportunity.location ?? 'Remote'}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h4>Continue preparing</h4>
                  <button className="text-button" onClick={() => setTab('checklist')}>Open checklist</button>
                </div>

                <div className="task-list">
                  {[
                    { title: 'Upload your updated resume', meta: 'Required before applying', priority: 'High' },
                    { title: 'Confirm graduation year', meta: 'Needed for eligibility review', priority: 'Medium' },
                    { title: 'Add Python project evidence', meta: 'Preferred skill criterion', priority: 'Medium' },
                  ].map((task) => (
                    <div key={task.title} className="task-item">
                      <div className="task-check" />
                      <div className="task-copy">
                        <strong>{task.title}</strong>
                        <span>{task.meta}</span>
                      </div>
                      <span className="priority-badge">{task.priority}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </div>
        )}

        {tab === 'explore' && (
          <div className="grid two-col wide">
            <div className="panel" style={{ padding: '1rem' }}>
              <div className="filter-row">
                <input
                  aria-label="Filter opportunities"
                  className="search-box long"
                  placeholder="Search internships, scholarships, jobs..."
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                />
                <button type="button" className="button-soft" onClick={() => setSelectedCategory('All')}>All categories</button>
                <button type="button" className="button-soft" onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('All');
                  setEligibilityFilter('All');
                }}>Reset</button>
              </div>

              <div className="chip-row">
                {['All', 'Internship', 'Job', 'Scholarship', 'Hackathon', 'Competition', 'Workshop'].map((label) => (
                  <button
                    key={label}
                    type="button"
                    className={`chip ${selectedCategory === label ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(label)}
                  >
                    {label}
                  </button>
                ))}
                <label className="filter-select-label">
                  Requirement fit
                  <select value={eligibilityFilter} onChange={(event) => setEligibilityFilter(event.target.value)}>
                    {['All', 'Eligible', 'Needs information', 'Not eligible'].map((fit) => <option key={fit}>{fit}</option>)}
                  </select>
                </label>
              </div>

              <div className="space-y-4">
                {filteredOpportunities.length ? filteredOpportunities.map((opportunity) => (
                  <div
                    key={opportunity.id}
                    role="button"
                    tabIndex={0}
                    className={`opportunity-card ${selectedOpportunityId === opportunity.id ? 'selected' : ''}`}
                    onClick={() => setSelectedOpportunityId(opportunity.id)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        setSelectedOpportunityId(opportunity.id);
                      }
                    }}
                  >
                    <div className="opportunity-head">
                      <div>
                        <div className="org-name">{opportunity.organization}</div>
                        <h4>{opportunity.title}</h4>
                      </div>
                      <div className="tag-row">
                        <span className="tag">{opportunity.category}</span>
                        <span className="bookmark">☆</span>
                      </div>
                    </div>

                    <p>{opportunity.description}</p>

                    <div className="meta-grid">
                      <span>Deadline: {opportunity.deadline ?? 'Not specified'}</span>
                      <span>Location: {opportunity.location ?? 'Remote'}</span>
                      <span>Remote: {opportunity.remote ?? 'Hybrid'}</span>
                      <span>Verified: {opportunity.verification_status ?? 'Unverified'}</span>
                      <span>Requirement fit: {eligibilityByOpportunity[opportunity.id] ?? 'Not analyzed'}</span>
                    </div>

                    <div className="action-row">
                      <button type="button" className="text-button">View details</button>
                      <button type="button" className="primary-button small" onClick={(event) => { event.stopPropagation(); setTab('analyze'); }}>Analyze fit</button>
                    </div>
                  </div>
                )) : (
                  <div className="empty-box">No opportunities match your search. Try another keyword or category.</div>
                )}
              </div>
            </div>

            <div className="panel detail-panel">
              <div className="detail-header">
                <div>
                  <span className="eyebrow muted">Opportunity detail</span>
                  <h3>{selectedOpportunity?.title ?? 'No matching opportunity'}</h3>
                </div>
                {selectedOpportunity && <span className="tag">{selectedOpportunity.category}</span>}
              </div>

              {selectedOpportunity ? <div className="detail-body">
                <p>{selectedOpportunity?.description}</p>

                <div className="detail-grid">
                  <div><label>Organization</label><strong>{selectedOpportunity?.organization}</strong></div>
                  <div><label>Deadline</label><strong>{selectedOpportunity?.deadline ?? 'Not specified'}</strong></div>
                  <div><label>Location</label><strong>{selectedOpportunity?.location ?? 'Remote'}</strong></div>
                  <div><label>Application</label><strong>{selectedOpportunity?.application_url ?? 'Not available'}</strong></div>
                </div>

                <div className="requirement-list">
                  {(selectedOpportunity?.requirements ?? []).map((requirement, index) => (
                    <div key={`${requirement.name}-${index}`} className="mini-rule">
                      <span>{requirement.name}</span>
                      <strong>{requirement.expected_value ?? 'Requirement'}</strong>
                    </div>
                  ))}
                </div>

                <div className="detail-actions">
                  <button className="secondary-button" onClick={() => selectedOpportunity && trackOpportunity(selectedOpportunity)}>Track application</button>
                  <button className="primary-button" onClick={() => setTab('analyze')}>Compare with my profile</button>
                </div>
                {applicationMessage && <p className="inline-message" role="status">{applicationMessage}</p>}
              </div> : <div className="detail-body"><div className="empty-box">No opportunity matches these filters.</div></div>}
            </div>
          </div>
        )}

        {tab === 'analyze' && (
          <div className="analysis-layout">
            <div className="panel">
              <div className="panel-header">
                <h4>Import or add opportunity</h4>
              </div>

              <div className="form-grid">
                <input value={newOpportunity.title} onChange={(e) => setNewOpportunity({ ...newOpportunity, title: e.target.value })} placeholder="Opportunity title" />
                <input value={newOpportunity.organization} onChange={(e) => setNewOpportunity({ ...newOpportunity, organization: e.target.value })} placeholder="Organization" />
                <select aria-label="Opportunity category" value={newOpportunity.category} onChange={(e) => setNewOpportunity({ ...newOpportunity, category: e.target.value })}>
                  {['internship', 'job', 'scholarship', 'fellowship', 'competition'].map((category) => <option key={category} value={category}>{category[0].toUpperCase() + category.slice(1)}</option>)}
                </select>
                <input value={newOpportunity.deadline} onChange={(e) => setNewOpportunity({ ...newOpportunity, deadline: e.target.value })} placeholder="Deadline" />
              </div>

              <textarea
                value={newOpportunity.description}
                onChange={(e) => setNewOpportunity({ ...newOpportunity, description: e.target.value })}
                placeholder="Paste the opportunity description here"
              />

              <div className="button-row">
                <button className="primary-button" onClick={extractFromText}>Extract requirements</button>
                <button className="secondary-button" onClick={addOpportunity}>Add opportunity</button>
              </div>

              <textarea
                value={manualText}
                onChange={(e) => setManualText(e.target.value)}
                placeholder="Paste a public URL or opportunity text for extraction"
                className="secondary-textarea"
              />

              {extractedRequirements.length > 0 && (
                <div className="extract-box">
                  <h5>Extracted requirements</h5>
                  {extractedRequirements.map((item, index) => (
                    <div key={`${item.name}-${index}`} className="extract-item">
                      <span>{item.name}</span>
                      <strong>{item.expected_value}</strong>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="panel">
              <div className="panel-header">
                <h4>Eligibility analysis</h4>
              </div>

              {analysis ? (
                <div className="analysis-body">
                  <div className="summary-box">
                    <div>
                      <span>Match</span>
                      <strong>{analysis.summary.match}</strong>
                    </div>
                    <div className="danger">
                      <span>Mismatch</span>
                      <strong>{analysis.summary.mismatch}</strong>
                    </div>
                    <div className="warning">
                      <span>Missing info</span>
                      <strong>{analysis.summary.missing}</strong>
                    </div>
                  </div>

                  <div className="requirement-list report-list">
                    {analysis.results.map((item: any, index: number) => (
                      <div key={`${item.name}-${index}`} className="report-row">
                        <div className="report-head">
                          <strong>{item.name}</strong>
                          <span className={`status-pill ${statusClass(item.evaluation_status)}`}>{item.evaluation_status}</span>
                        </div>
                        <p>{item.explanation}</p>
                        <small>Recommended action: {item.recommended_action}</small>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="empty-box">Run an analysis to see the requirement-by-requirement report.</div>
              )}
            </div>
          </div>
        )}

        {tab === 'checklist' && (
          <div className="panel">
            <div className="panel-header checklist-header">
              <div>
                <h4>Opportunity requirement checklist</h4>
                <p className="muted-copy">Compare eligibility, skills, documents, and deadlines with your profile.</p>
              </div>
              <label className="checklist-opportunity-picker">
                Opportunity
                <select
                  aria-label="Choose opportunity checklist"
                  value={checklistOpportunity?.id ?? ''}
                  onChange={(event) => {
                    const opportunityId = Number(event.target.value);
                    setChecklistOpportunityId(opportunityId);
                    setSelectedOpportunityId(opportunityId);
                  }}
                >
                  {opportunities.map((opportunity) => (
                    <option key={opportunity.id} value={opportunity.id}>{opportunity.title} · {opportunity.category}</option>
                  ))}
                </select>
              </label>
            </div>

            {checklistOpportunity ? (
              <>
                <div className="checklist-opportunity-summary">
                  <div>
                    <span>{checklistOpportunity.organization} · {checklistOpportunity.category}</span>
                    <strong>{checklistOpportunity.title}</strong>
                  </div>
                  <div>
                    <span>Application deadline</span>
                    <strong>{checklistOpportunity.deadline ?? 'Not provided'}</strong>
                  </div>
                </div>

                {checklistAnalysis ? (
                  <>
                    <div className="summary-box checklist-summary">
                      <div><span>Match</span><strong>{checklistStatusCounts.match}</strong></div>
                      <div className="danger"><span>Mismatch</span><strong>{checklistStatusCounts.mismatch}</strong></div>
                      <div className="warning"><span>Missing information</span><strong>{checklistStatusCounts.missing}</strong></div>
                    </div>
                    <p className="checklist-summary-copy">
                      {checklistStatusCounts.mismatch > 0
                        ? `${checklistStatusCounts.mismatch} requirement${checklistStatusCounts.mismatch === 1 ? '' : 's'} do not currently match. Review the reasons and next steps below.`
                        : checklistStatusCounts.missing > 0
                          ? `${checklistStatusCounts.missing} requirement${checklistStatusCounts.missing === 1 ? '' : 's'} need more information. Add the missing details before deciding whether you qualify.`
                          : 'All listed requirements currently match your profile.'}
                    </p>

                    <div className="checklist-results">
                      {checklistResults.map((item, index) => (
                        <article key={`${item.name}-${index}`} className="checklist-result">
                          <div className="checklist-result-header">
                            <div>
                              <span className="checklist-category">{String(item.category ?? 'general').replace(/_/g, ' ')}</span>
                              <h5>{item.name}</h5>
                              <span className="checklist-expected">{item.expected_value ?? 'Requirement details not provided'}</span>
                            </div>
                            <span className={`status-pill ${statusClass(item.evaluation_status)}`}>{statusLabel(item.evaluation_status)}</span>
                          </div>
                          <p>{item.explanation}</p>
                          <small>Next step: {item.recommended_action}</small>
                        </article>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="empty-box">Requirement analysis is unavailable. Start the API and try again to compare this checklist with your profile.</div>
                )}
              </>
            ) : (
              <div className="empty-box">Add or load an opportunity to build its requirement checklist.</div>
            )}
          </div>
        )}

        {tab === 'tracker' && (
          <div className="panel">
            <div className="panel-header">
              <h4>Application tracker</h4>
              <button className="secondary-button" onClick={() => setTab('explore')}>Find opportunities</button>
            </div>

            <div className="tracker-list">
              {applications.length ? applications.map((application) => {
                const opportunity = opportunities.find((item) => item.id === application.opportunity_id);
                if (!opportunity) return null;
                return (
                <div key={application.id} className="tracker-row">
                  <div>
                    <strong>{opportunity.title}</strong>
                    <span>{opportunity.organization}</span>
                  </div>
                  <select aria-label={`Application status for ${opportunity.title}`} value={application.status} onChange={(event) => updateApplicationStatus(application, event.target.value)}>
                    {['saved', 'preparing documents', 'applied', 'interview', 'offer', 'rejected'].map((status) => <option key={status} value={status}>{status}</option>)}
                  </select>
                  <span>{opportunity.deadline ?? 'No deadline'}</span>
                </div>
              ); }) : <div className="empty-box">Your tracker is empty. Add a job or internship from Explore Opportunities.</div>}
            </div>
            {applicationMessage && <p className="inline-message" role="status">{applicationMessage}</p>}
          </div>
        )}

        {tab === 'resume' && (
          <div className="resume-layout">
            <section className="panel resume-editor">
              <div className="panel-header">
                <div>
                  <h4>Build your resume</h4>
                  <p className="muted-copy">Your resume is saved in this browser. Use Print / Save PDF to export it.</p>
                </div>
                <button className="primary-button small" onClick={() => window.print()}>Print / Save PDF</button>
              </div>
              {resumeSaveError && <p className="inline-message error-message" role="alert">{resumeSaveError}</p>}
              <div className="resume-fields">
                {([
                  ['fullName', 'Full name', 'text'],
                  ['email', 'Email', 'email'],
                  ['phone', 'Phone', 'tel'],
                  ['location', 'Location', 'text'],
                  ['headline', 'Professional headline', 'text'],
                ] as const).map(([field, label, type]) => (
                  <label key={field}>{label}<input type={type} value={resume[field]} onChange={(event) => updateResume(field, event.target.value)} /></label>
                ))}
                {([
                  ['summary', 'Profile summary'],
                  ['education', 'Education (one entry per line)'],
                  ['skills', 'Skills (one per line or comma-separated)'],
                  ['projects', 'Projects (one project per line)'],
                  ['experience', 'Experience / volunteering (one entry per line)'],
                  ['certifications', 'Certifications (one per line)'],
                  ['links', 'Portfolio and profile links (one per line)'],
                ] as const).map(([field, label]) => (
                  <label key={field}>{label}<textarea value={resume[field]} onChange={(event) => updateResume(field, event.target.value)} /></label>
                ))}
              </div>
            </section>
            <section className="resume-preview" aria-label="Resume preview">
              <div className="resume-preview-header">
                <h1>{resume.fullName || 'Your name'}</h1>
                <p>{[resume.email, resume.phone, resume.location].filter(Boolean).join('  ·  ') || 'Email · Phone · Location'}</p>
                {resume.headline && <strong>{resume.headline}</strong>}
              </div>
              {resume.summary && <section><h2>Profile</h2><p>{resume.summary}</p></section>}
              {resume.education && <section><h2>Education</h2>{resumeLines(resume.education).map((line, index) => <p key={index}>{line}</p>)}</section>}
              {resume.skills && <section><h2>Skills</h2><p>{resume.skills.split(/[,\n]/).map((skill) => skill.trim()).filter(Boolean).join(' · ')}</p></section>}
              {([
                ['Projects', resume.projects],
                ['Experience', resume.experience],
                ['Certifications', resume.certifications],
                ['Links', resume.links],
              ] as const).map(([heading, content]) => content && (
                <section key={heading}><h2>{heading}</h2><ul>{resumeLines(content).map((line, index) => <li key={index}>{line}</li>)}</ul></section>
              ))}
              {!resume.summary && !resume.education && !resume.skills && !resume.projects && !resume.experience && !resume.certifications && (
                <p className="resume-placeholder">Complete the sections to see your resume preview.</p>
              )}
            </section>
          </div>
        )}

        {tab === 'profile' && profile && (
          <div className="panel">
            <div className="panel-header">
              <h4>Student profile</h4>
              <button className="primary-button small" onClick={saveProfile}>Save profile</button>
            </div>

            <div className="form-grid two-col-form">
              <input value={profile.name} onChange={(e) => handleProfileChange('name', e.target.value)} placeholder="Name" />
              <input value={profile.email} onChange={(e) => handleProfileChange('email', e.target.value)} placeholder="Email" />
              <input value={profile.college} onChange={(e) => handleProfileChange('college', e.target.value)} placeholder="College" />
              <input value={profile.degree} onChange={(e) => handleProfileChange('degree', e.target.value)} placeholder="Degree" />
              <input value={profile.department} onChange={(e) => handleProfileChange('department', e.target.value)} placeholder="Department" />
              <input value={profile.current_year} onChange={(e) => handleProfileChange('current_year', e.target.value)} placeholder="Academic year" />
              <input type="number" value={profile.graduation_year ?? ''} onChange={(e) => handleProfileChange('graduation_year', e.target.value === '' ? null : Number(e.target.value))} placeholder="Graduation year" />
              <input type="number" step="0.1" value={profile.cgpa ?? ''} onChange={(e) => handleProfileChange('cgpa', e.target.value === '' ? null : Number(e.target.value))} placeholder="CGPA" />
              <input type="number" step="0.1" value={profile.marks ?? ''} onChange={(e) => handleProfileChange('marks', e.target.value === '' ? null : Number(e.target.value))} placeholder="Marks / percentage" />
              <input type="number" value={profile.annual_income ?? ''} onChange={(e) => handleProfileChange('annual_income', e.target.value === '' ? null : Number(e.target.value))} placeholder="Annual family income (₹)" />
              <input type="number" min="1" value={profile.team_size ?? ''} onChange={(e) => handleProfileChange('team_size', e.target.value === '' ? null : Number(e.target.value))} placeholder="Competition team size" />
              <input value={profile.skills.join(', ')} onChange={(e) => handleProfileChange('skills', e.target.value.split(',').map((item) => item.trim()))} placeholder="Skills" />
              <input value={profile.projects?.join(', ') ?? ''} onChange={(e) => handleProfileChange('projects', e.target.value.split(',').map((item) => item.trim()))} placeholder="Projects / portfolio items" />
              <input value={profile.resume_url} onChange={(e) => handleProfileChange('resume_url', e.target.value)} placeholder="Resume URL" />
              <input value={profile.github_url} onChange={(e) => handleProfileChange('github_url', e.target.value)} placeholder="GitHub URL" />
              <input value={profile.linkedin_url} onChange={(e) => handleProfileChange('linkedin_url', e.target.value)} placeholder="LinkedIn URL" />
            </div>
            <div className="document-readiness">
              <h5>Document readiness</h5>
              <p className="muted-copy">Keep unknown documents unconfirmed; mark only documents you have checked.</p>
              {([
                ['resume', 'Resume'],
                ['transcript', 'Academic transcript'],
                ['income', 'Income certificate'],
                ['portfolio', 'Portfolio'],
              ] as const).map(([key, label]) => {
                const value = profile.documents?.[key];
                const readiness = value === undefined ? 'unknown' : value === false || ['no', 'missing', 'not uploaded', 'not ready'].includes(String(value).toLowerCase()) ? 'not_ready' : 'ready';
                return (
                  <label key={key} className="document-readiness-row">
                    <span>{label}</span>
                    <select
                      aria-label={`${label} readiness`}
                      value={readiness}
                      onChange={(event) => {
                        const documents = { ...profile.documents };
                        if (event.target.value === 'unknown') delete documents[key];
                        else documents[key] = event.target.value === 'ready' ? 'ready' : false;
                        handleProfileChange('documents', documents);
                      }}
                    >
                      <option value="unknown">Not confirmed</option>
                      <option value="ready">Ready</option>
                      <option value="not_ready">Not ready</option>
                    </select>
                  </label>
                );
              })}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
