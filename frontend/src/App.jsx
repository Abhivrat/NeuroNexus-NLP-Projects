
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  FileText,
  BrainCircuit,
  Target,
  History as HistoryIcon,
  Settings,
  Bell,
  Search,
  UploadCloud,
  ArrowUpRight,
  CheckCircle2,
  AlertCircle,
  Zap,
  Menu,
  X,
  Sparkles,
  Download,
  BriefcaseBusiness,
  ChevronRight,
  Trash2,
  Eye,
  RefreshCw,
} from "lucide-react";
import axios from "axios";
import "./App.css";

const API = "https://neuronexus-ai-backend.onrender.com";

function App() {
  const [active, setActive] = useState("Dashboard");
  const [file, setFile] = useState(null);
  const [job, setJob] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const [search, setSearch] = useState("");

  const [historyItems, setHistoryItems] = useState(() => {
    try {
      return JSON.parse(
        localStorage.getItem("neuronexus_history") || "[]"
      );
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem(
      "neuronexus_history",
      JSON.stringify(historyItems)
    );
  }, [historyItems]);

  const navigation = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Resume Analyzer", icon: FileText },
    { name: "AI Insights", icon: BrainCircuit },
    { name: "Job Matching", icon: Target },
    { name: "History", icon: HistoryIcon },
    { name: "Settings", icon: Settings },
  ];

  const score = Number(result?.overall_score ?? 0);
  const matchedSkills = result?.matched_skills || [];
  const missingSkills = result?.missing_skills || [];
  const recommendations = result?.recommendations || [];

  function navigate(page) {
    setActive(page);
    setMenuOpen(false);
    setError("");
  }

  async function analyzeResume(e) {
    e.preventDefault();

    if (!file || !job.trim()) {
      setError("Please upload a resume and enter a job description.");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("File size must be less than 10 MB.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const data = new FormData();
    data.append("file", file);
    data.append("job_description", job);

    try {
      const response = await axios.post(
        `${API}/api/resume/analyze`,
        data
      );

      const analysis = response.data.results;

      if (!analysis) {
        throw new Error("The server returned an invalid analysis result.");
      }

      setResult(analysis);

      const historyEntry = {
        id: Date.now(),
        filename: file.name,
        job,
        date: new Date().toLocaleString(),
        results: analysis,
      };

      setHistoryItems((previous) => [
        historyEntry,
        ...previous,
      ]);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Could not connect to the analysis server. Check that your backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  async function exportReport(
    data = result,
    reportFilename = "NeuroNexus-Resume-Report.pdf",
    reportJob = job,
    resumeFilename = file?.name || "Resume"
  ) {
    if (!data) {
      window.alert("Please analyze a resume before exporting.");
      return;
    }

    try {
      const response = await axios.post(
        `${API}/api/resume/report`,
        {
          filename: resumeFilename,
          job_description: reportJob,
          results: data,
        },
        {
          responseType: "blob",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const blob = new Blob([response.data], {
        type: "application/pdf",
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = reportFilename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("PDF export error:", err);

      // When FastAPI returns an error with responseType: "blob",
      // its JSON detail may arrive as a Blob. Try to show that detail.
      let message = "Could not generate PDF. Please check that your backend is running.";
      if (err.response?.data instanceof Blob) {
        try {
          const errorData = JSON.parse(await err.response.data.text());
          message = errorData.detail || message;
        } catch {
          // Keep the fallback message if the response is not JSON.
        }
      }
      window.alert(message);
    }
  }

  function openHistoryItem(item) {
    setResult(item.results);
    setJob(item.job || "");
    setFile(null);
    navigate("Resume Analyzer");
  }

  function deleteHistoryItem(id) {
    setHistoryItems((previous) =>
      previous.filter((item) => item.id !== id)
    );
  }

  function clearHistory() {
    if (window.confirm("Are you sure you want to delete all analysis history?")) {
      setHistoryItems([]);
    }
  }

  const filteredHistory = historyItems.filter((item) =>
    `${item.filename} ${item.job}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  const statItems = [
    {
      label: "Resume Score",
      value: result ? `${score}%` : "—",
      note: "Your latest analysis",
      icon: FileText,
      color: "purple",
    },
    {
      label: "Job Compatibility",
      value: result
        ? `${result.semantic_similarity ?? 0}%`
        : "—",
      note: "Semantic job match",
      icon: Target,
      color: "blue",
    },
    {
      label: "Skills Matched",
      value: result ? matchedSkills.length : "—",
      note: "Relevant skills found",
      icon: CheckCircle2,
      color: "green",
    },
    {
      label: "Skills to Improve",
      value: result ? missingSkills.length : "—",
      note: "Potential skill gaps",
      icon: BrainCircuit,
      color: "orange",
    },
  ];

  function DashboardPage() {
    return (
      <>
        <motion.div
          className="welcome-row"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div>
            <div className="eyebrow">
              <Sparkles size={14} /> YOUR AI CAREER COMPANION
            </div>
            <h1>
              Build your next <span>career move.</span>
            </h1>
            <p>
              Analyze your resume, discover skill gaps, and move
              closer to your dream role.
            </p>
          </div>
          <div className="date-pill">
            <Zap size={15} /> AI ENGINE READY
          </div>
        </motion.div>

        <section className="stats-grid">
          {statItems.map((item, index) => (
            <motion.div
              className="stat-card"
              key={item.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.09 }}
            >
              <div className="stat-top">
                <span>{item.label}</span>
                <div className={`stat-icon ${item.color}`}>
                  <item.icon size={19} />
                </div>
              </div>
              <h2>{item.value}</h2>
              <small>{item.note}</small>
            </motion.div>
          ))}
        </section>

        <div className="section-heading">
          <div>
            <h2>Resume Intelligence</h2>
            <p>Analyze your profile against your target opportunity.</p>
          </div>
          <span className="live-label">
            <span /> LIVE ANALYSIS
          </span>
        </div>

        <AnalysisWorkspace />

        {result && <ResultsPanel />}

        <BottomPanels />
      </>
    );
  }

  function AnalysisWorkspace() {
    return (
      <section className="analysis-grid">
        <motion.div
          className="panel upload-panel"
          initial={{ opacity: 0, x: -15 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="panel-title">
            <div className="panel-icon">
              <UploadCloud />
            </div>
            <div>
              <h3>Upload your resume</h3>
              <p>Let AI understand your experience.</p>
            </div>
          </div>

          <form onSubmit={analyzeResume}>
            <label className="dropzone">
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(e) => {
                  setFile(e.target.files?.[0] || null);
                  setError("");
                }}
              />
              <UploadCloud size={31} />
              <strong>
                {file ? file.name : "Drop your resume here"}
              </strong>
              <span>
                {file
                  ? "File selected successfully"
                  : "or click to browse your files"}
              </span>
              <small>PDF or DOCX · Maximum 10 MB</small>
            </label>

            <label className="field-label" htmlFor="job-description">
              TARGET JOB DESCRIPTION
            </label>

            <textarea
              id="job-description"
              value={job}
              onChange={(e) => setJob(e.target.value)}
              placeholder="Paste the job description here. Include required skills, experience and responsibilities..."
              rows={5}
            />

            {error && (
              <div className="error-message">
                <AlertCircle size={16} /> {error}
              </div>
            )}

            <button
              className="analyze-button"
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Analyzing your resume..."
                : "Analyze with NeuroNexus"}
              {!loading && <Sparkles size={17} />}
            </button>
          </form>

          <div className="privacy-note">
            <CheckCircle2 size={14} />
            Your resume is processed for analysis only.
          </div>
        </motion.div>

        <motion.div
          className="panel score-panel"
          initial={{ opacity: 0, x: 15 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="panel-title">
            <div className="panel-icon purple-bg">
              <BrainCircuit />
            </div>
            <div>
              <h3>AI Analysis Overview</h3>
              <p>Your resume performance snapshot.</p>
            </div>
          </div>

          <div
            className="score-circle"
            style={{ "--score": `${score * 3.6}deg` }}
          >
            <div>
              <strong>{result ? score : "—"}</strong>
              <span>{result ? "OUT OF 100" : "NO ANALYSIS"}</span>
            </div>
          </div>

          <div className="score-caption">
            {result
              ? "Your resume match score"
              : "Your results will appear here"}
          </div>

          {result ? (
            <div className="result-details">
              <div>
                <span>Semantic similarity</span>
                <strong>{result.semantic_similarity}%</strong>
              </div>
              <div>
                <span>Skill match</span>
                <strong>{result.skill_match}%</strong>
              </div>
            </div>
          ) : (
            <div className="empty-hint">
              <Sparkles size={16} />
              Upload a resume to unlock your AI insights.
            </div>
          )}
        </motion.div>
      </section>
    );
  }

  function ResultsPanel() {
    return (
      <motion.section
        className="panel results-panel"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="section-heading">
          <div>
            <h2>Analysis Results</h2>
            <p>Insights generated from your resume.</p>
          </div>
          <button
            className="export-button"
            onClick={() => exportReport()}
          >
            <Download size={16} /> Export report
          </button>
        </div>

        <div className="skills-columns">
          <div>
            <h3>
              <CheckCircle2 /> Matched Skills
            </h3>
            <div className="skill-list">
              {matchedSkills.length ? (
                matchedSkills.map((skill) => (
                  <span className="skill matched" key={skill}>
                    {skill}
                  </span>
                ))
              ) : (
                <p>No matched skills found.</p>
              )}
            </div>
          </div>

          <div>
            <h3>
              <Target /> Skills to Improve
            </h3>
            <div className="skill-list">
              {missingSkills.length ? (
                missingSkills.map((skill) => (
                  <span className="skill missing" key={skill}>
                    {skill}
                  </span>
                ))
              ) : (
                <p>No missing skills found.</p>
              )}
            </div>
          </div>
        </div>

        <div className="recommendations">
          <h3>
            <Sparkles /> AI Recommendations
          </h3>
          {recommendations.length ? (
            recommendations.map((recommendation, index) => (
              <p key={index}>
                <ArrowUpRight size={15} /> {recommendation}
              </p>
            ))
          ) : (
            <p>No recommendations available.</p>
          )}
        </div>
      </motion.section>
    );
  }

  function BottomPanels() {
    return (
      <section className="bottom-grid">
        <div className="panel tip-panel">
          <div className="tip-icon">
            <Zap />
          </div>
          <div>
            <span>CAREER TIP OF THE DAY</span>
            <h3>Show impact, not just responsibilities.</h3>
            <p>
              Use measurable achievements in your resume. Numbers
              help recruiters understand the value you bring.
            </p>
          </div>
        </div>

        <div className="panel quick-panel">
          <div>
            <BriefcaseBusiness size={20} />
            <h3>Ready for your next opportunity?</h3>
          </div>
          <p>
            Start with a targeted resume analysis and make every
            application count.
          </p>
          <button onClick={() => {
            navigate("Resume Analyzer");
            document.querySelector(".dropzone")?.scrollIntoView({
              behavior: "smooth",
            });
          }}>
            Start analyzing <ArrowUpRight size={16} />
          </button>
        </div>
      </section>
    );
  }

  function InsightsPage() {
    return (
      <>
        <PageHeading
          title="AI Career Insights"
          description="Understand your strengths, skill gaps and opportunities."
        />

        {!result ? (
          <EmptyPage
            title="No insights available yet"
            description="Analyze your resume first to unlock personalized AI career insights."
            action="Analyze Resume"
            onClick={() => navigate("Resume Analyzer")}
          />
        ) : (
          <>
            <section className="stats-grid">
              {statItems.map((item) => (
                <div className="stat-card" key={item.label}>
                  <div className="stat-top">
                    <span>{item.label}</span>
                    <div className={`stat-icon ${item.color}`}>
                      <item.icon size={19} />
                    </div>
                  </div>
                  <h2>{item.value}</h2>
                  <small>{item.note}</small>
                </div>
              ))}
            </section>

            <section className="panel results-panel">
              <h2>Your strengths</h2>
              <p>Skills detected in your resume and relevant to the job.</p>
              <div className="skill-list">
                {matchedSkills.map((skill) => (
                  <span className="skill matched" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>

              <div className="recommendations">
                <h3><Sparkles /> AI Recommendations</h3>
                {recommendations.map((item, index) => (
                  <p key={index}>
                    <ArrowUpRight size={15} /> {item}
                  </p>
                ))}
              </div>

              <h3>Skills to develop</h3>
              <div className="skill-list">
                {missingSkills.map((skill) => (
                  <span className="skill missing" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>
            </section>
          </>
        )}
      </>
    );
  }

  function JobMatchingPage() {
    return (
      <>
        <PageHeading
          title="Job Matching"
          description="See how well your resume matches your target job."
        />

        {!result ? (
          <EmptyPage
            title="No job match available"
            description="Upload a resume and provide a job description to calculate your compatibility."
            action="Start Analysis"
            onClick={() => navigate("Resume Analyzer")}
          />
        ) : (
          <>
            <section className="stats-grid">
              <div className="stat-card">
                <div className="stat-top">
                  <span>Job Compatibility</span>
                  <Target />
                </div>
                <h2>{result.semantic_similarity ?? 0}%</h2>
                <small>Semantic job match</small>
              </div>

              <div className="stat-card">
                <div className="stat-top">
                  <span>Skill Match</span>
                  <CheckCircle2 />
                </div>
                <h2>{result.skill_match ?? 0}%</h2>
                <small>Relevant skills detected</small>
              </div>

              <div className="stat-card">
                <div className="stat-top">
                  <span>Matched Skills</span>
                  <BrainCircuit />
                </div>
                <h2>{matchedSkills.length}</h2>
                <small>Skills in your resume</small>
              </div>
            </section>

            <section className="panel results-panel">
              <h2>Job Description Used</h2>
              <p style={{ whiteSpace: "pre-wrap" }}>{job}</p>

              <div className="skills-columns">
                <div>
                  <h3><CheckCircle2 /> Matching Skills</h3>
                  <div className="skill-list">
                    {matchedSkills.map((skill) => (
                      <span className="skill matched" key={skill}>
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3><Target /> Missing Skills</h3>
                  <div className="skill-list">
                    {missingSkills.map((skill) => (
                      <span className="skill missing" key={skill}>
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          </>
        )}
      </>
    );
  }

  function HistoryPage() {
    return (
      <>
        <PageHeading
          title="Analysis History"
          description="Review and reopen your previous resume analyses."
        />

        <section className="panel results-panel">
          <div className="section-heading">
            <div>
              <h2>Previous Analyses</h2>
              <p>{historyItems.length} saved analysis records</p>
            </div>

            {historyItems.length > 0 && (
              <button
                className="export-button"
                onClick={clearHistory}
              >
                <Trash2 size={16} /> Clear History
              </button>
            )}
          </div>

          <div style={{ margin: "20px 0" }}>
            <input
              type="text"
              placeholder="Search by resume name or job description..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                width: "100%",
                padding: "14px",
                borderRadius: "10px",
                background: "#111426",
                color: "white",
                border: "1px solid #30344c",
              }}
            />
          </div>

          {filteredHistory.length === 0 ? (
            <div style={{ padding: "35px 10px", textAlign: "center" }}>
              <HistoryIcon size={35} />
              <h3>No analysis history found</h3>
              <p>
                Your completed resume analyses will appear here.
              </p>
              <button
                className="analyze-button"
                onClick={() => navigate("Resume Analyzer")}
              >
                Analyze a Resume <ArrowUpRight size={16} />
              </button>
            </div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{
                width: "100%",
                borderCollapse: "collapse",
                textAlign: "left",
              }}>
                <thead>
                  <tr>
                    <th style={{ padding: "14px" }}>Resume</th>
                    <th style={{ padding: "14px" }}>Date</th>
                    <th style={{ padding: "14px" }}>Score</th>
                    <th style={{ padding: "14px" }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredHistory.map((item) => (
                    <tr key={item.id}>
                      <td style={{ padding: "14px" }}>
                        <strong>{item.filename}</strong>
                      </td>
                      <td style={{ padding: "14px" }}>
                        {item.date}
                      </td>
                      <td style={{ padding: "14px" }}>
                        {item.results?.overall_score ?? 0}%
                      </td>
                      <td style={{ padding: "14px" }}>
                        <button
                          className="export-button"
                          onClick={() => openHistoryItem(item)}
                          title="View analysis"
                        >
                          <Eye size={15} /> View
                        </button>
                        <button
                          className="export-button"
                          onClick={() => exportReport(
                            item.results,
                            `NeuroNexus-${item.filename}-Report.pdf`,
                            item.job,
                            item.filename
                          )}
                          title="Download report"
                        >
                          <Download size={15} />
                        </button>
                        <button
                          className="export-button"
                          onClick={() => deleteHistoryItem(item.id)}
                          title="Delete record"
                        >
                          <Trash2 size={15} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </>
    );
  }

  function SettingsPage() {
    return (
      <>
        <PageHeading
          title="Settings"
          description="Manage your NeuroNexus workspace."
        />

        <section className="panel results-panel">
          <h2>Workspace Settings</h2>

          <div style={{ marginTop: "25px" }}>
            <h3>Profile</h3>
            <p>NeuroNexus User</p>
            <p>Free workspace</p>
          </div>

          <hr style={{ margin: "25px 0", opacity: 0.15 }} />

          <div>
            <h3>Analysis Data</h3>
            <p>
              You currently have {historyItems.length} saved
              analyses in this browser.
            </p>
            <button
              className="export-button"
              onClick={clearHistory}
              disabled={historyItems.length === 0}
            >
              <Trash2 size={16} /> Clear All Analysis History
            </button>
          </div>

          <hr style={{ margin: "25px 0", opacity: 0.15 }} />

          <div>
            <h3>Application Information</h3>
            <p>NeuroNexus AI Career Intelligence</p>
            <p>Version 1.0.0</p>
            <p>React + FastAPI + NLP</p>
          </div>
        </section>
      </>
    );
  }

  function PageHeading({ title, description }) {
    return (
      <div className="welcome-row">
        <div>
          <div className="eyebrow">
            <Sparkles size={14} /> NEURONEXUS WORKSPACE
          </div>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>
        <div className="date-pill">
          <Zap size={15} /> AI ENGINE READY
        </div>
      </div>
    );
  }

  function EmptyPage({ title, description, action, onClick }) {
    return (
      <section className="panel results-panel" style={{
        textAlign: "center",
        padding: "55px 25px",
      }}>
        <BrainCircuit size={45} />
        <h2>{title}</h2>
        <p>{description}</p>
        <button className="analyze-button" onClick={onClick}>
          {action} <ArrowUpRight size={16} />
        </button>
      </section>
    );
  }

  function CurrentPage() {
    switch (active) {
      case "Dashboard":
      case "Resume Analyzer":
        return <DashboardPage />;
      case "AI Insights":
        return <InsightsPage />;
      case "Job Matching":
        return <JobMatchingPage />;
      case "History":
        return <HistoryPage />;
      case "Settings":
        return <SettingsPage />;
      default:
        return <DashboardPage />;
    }
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${menuOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon">
            <BrainCircuit size={25} />
          </div>
          <div>
            <h2>NeuroNexus<span>.</span></h2>
            <small>AI CAREER INTELLIGENCE</small>
          </div>
          <button
            className="mobile-close"
            onClick={() => setMenuOpen(false)}
          >
            <X />
          </button>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <nav>
          {navigation.map(({ name, icon: Icon }) => (
            <button
              key={name}
              className={`nav-link ${active === name ? "active" : ""}`}
              onClick={() => navigate(name)}
            >
              <Icon size={19} />
              <span>{name}</span>
              {name === "AI Insights" && (
                <span className="new-tag">NEW</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="pro-card">
            <Sparkles size={20} />
            <h3>Unlock your potential</h3>
            <p>
              Get smarter career insights with AI-powered analysis.
            </p>
            <button onClick={() => navigate("AI Insights")}>
              Explore insights <ArrowUpRight size={15} />
            </button>
          </div>

          <div className="profile">
            <div className="avatar">NN</div>
            <div>
              <strong>NeuroNexus User</strong>
              <small>Free workspace</small>
            </div>
            <button
              onClick={() => navigate("Settings")}
              aria-label="Open settings"
            >
              <Settings size={17} />
            </button>
          </div>
        </div>
      </aside>

      {menuOpen && (
        <div
          className="mobile-overlay"
          onClick={() => setMenuOpen(false)}
        />
      )}

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="menu-button"
              onClick={() => setMenuOpen(true)}
            >
              <Menu />
            </button>

            <div className="breadcrumb">
              Workspace <ChevronRight size={15} />
              <strong>{active}</strong>
            </div>
          </div>

          <div className="topbar-actions">
            <div className="search-box">
              <Search size={17} />
              <input
                placeholder="Search history..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  if (active !== "History") setActive("History");
                }}
              />
              <kbd>⌘ K</kbd>
            </div>

            <button
              className="icon-button"
              aria-label="Notifications"
              title="Notifications"
              onClick={() => window.alert("You are all caught up!")}
            >
              <Bell size={19} />
            </button>

            <div className="top-avatar">NN</div>
          </div>
        </header>

        <div className="page-content">
          <CurrentPage />

          <footer>
            © 2026 NeuroNexus AI
            <span>Built for smarter career decisions.</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
