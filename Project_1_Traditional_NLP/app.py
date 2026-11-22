import html
import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analyzer import extract_resume_text, analyze_resume, extract_skills


# ============================================================
# CONFIGURATION
# ============================================================
APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "neuronexus.db"

st.set_page_config(
    page_title="NeuroNexus | AI Career Assistant",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# All job listings below are sample/demo records stored locally.
# They are NOT live vacancies and are labelled as such in the Jobs page.
JOBS = [
    {
        "id": "NN001", "title": "Python Developer Intern", "company": "TechNova Demo",
        "location": "Gurugram, Haryana", "type": "Internship", "level": "Fresher",
        "skills": ["python", "sql", "git", "flask", "problem solving"],
        "description": "Build Python applications, work with APIs and SQL databases, write tests, use Git, and collaborate with a software team.",
    },
    {
        "id": "NN002", "title": "Machine Learning Intern", "company": "DataSphere Demo",
        "location": "Delhi NCR", "type": "Internship", "level": "Fresher",
        "skills": ["python", "machine learning", "pandas", "numpy", "scikit-learn", "statistics"],
        "description": "Prepare datasets, train machine learning models, evaluate results, and communicate insights using Python, Pandas, NumPy and Scikit-learn.",
    },
    {
        "id": "NN003", "title": "NLP Research Intern", "company": "LanguageLab Demo",
        "location": "Remote (India)", "type": "Internship", "level": "Fresher",
        "skills": ["python", "nlp", "natural language processing", "deep learning", "pytorch", "transformers"],
        "description": "Experiment with NLP pipelines, text classification, embeddings, transformer models and model evaluation.",
    },
    {
        "id": "NN004", "title": "Data Analyst Intern", "company": "InsightWorks Demo",
        "location": "Gurugram, Haryana", "type": "Internship", "level": "Fresher",
        "skills": ["python", "sql", "excel", "power bi", "data analysis", "data visualization"],
        "description": "Clean and analyze business datasets, write SQL queries, create dashboards and present data-driven findings.",
    },
    {
        "id": "NN005", "title": "Computer Vision Intern", "company": "VisionForge Demo",
        "location": "Noida, Uttar Pradesh", "type": "Internship", "level": "Fresher",
        "skills": ["python", "opencv", "computer vision", "deep learning", "tensorflow"],
        "description": "Build image-processing pipelines, experiment with object detection and evaluate computer vision models.",
    },
    {
        "id": "NN006", "title": "Junior Full Stack Developer", "company": "WebNest Demo",
        "location": "Delhi NCR", "type": "Full-time", "level": "Entry level",
        "skills": ["python", "javascript", "react", "html", "css", "mongodb", "rest api", "git"],
        "description": "Develop web application features using React, Python services, REST APIs, MongoDB, HTML and CSS.",
    },
    {
        "id": "NN007", "title": "AI/ML Project Trainee", "company": "NextGen AI Demo",
        "location": "Remote (India)", "type": "Trainee", "level": "Fresher",
        "skills": ["python", "artificial intelligence", "machine learning", "pandas", "scikit-learn", "git"],
        "description": "Support AI/ML prototypes, prepare data, build baseline models, document experiments and present project outcomes.",
    },
]

INTERVIEW_QUESTIONS = {
    "Python Developer": [
        {"q": "What is the difference between a list and a tuple in Python?", "keywords": ["mutable", "immutable", "change", "modify"]},
        {"q": "Explain how a Python dictionary works and when you would use it.", "keywords": ["key", "value", "hash", "lookup"]},
        {"q": "How would you handle an exception in Python?", "keywords": ["try", "except", "finally", "error"]},
    ],
    "Machine Learning": [
        {"q": "Explain overfitting and two ways to reduce it.", "keywords": ["training", "validation", "regularization", "cross validation", "data"]},
        {"q": "What is the difference between supervised and unsupervised learning?", "keywords": ["label", "labeled", "unlabeled", "target", "cluster"]},
        {"q": "Why do we split data into training and testing sets?", "keywords": ["unseen", "generalization", "evaluate", "performance", "test"]},
    ],
    "NLP Engineer": [
        {"q": "What is tokenization in NLP, and why is it needed?", "keywords": ["text", "tokens", "words", "sentences", "preprocess"]},
        {"q": "How are TF-IDF and transformer embeddings different?", "keywords": ["frequency", "context", "semantic", "embedding", "vector"]},
        {"q": "What is attention in a Transformer model?", "keywords": ["context", "weights", "tokens", "relationship", "sequence"]},
    ],
    "Data Analyst": [
        {"q": "How would you handle missing values in a dataset?", "keywords": ["remove", "impute", "mean", "median", "missing"]},
        {"q": "What is the difference between an INNER JOIN and a LEFT JOIN?", "keywords": ["matching", "all", "rows", "table", "null"]},
        {"q": "How would you explain a dashboard insight to a non-technical stakeholder?", "keywords": ["audience", "visual", "impact", "clear", "decision"]},
    ],
}


# ============================================================
# DATABASE
# ============================================================
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                resume_name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                overall_score REAL NOT NULL,
                job_similarity REAL NOT NULL,
                skill_coverage REAL NOT NULL,
                keyword_coverage REAL NOT NULL,
                resume_structure REAL NOT NULL,
                matched_skills TEXT NOT NULL,
                missing_skills TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                resume_skills TEXT NOT NULL DEFAULT '[]'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interview_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                role TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                score INTEGER NOT NULL,
                feedback TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS saved_jobs (
                job_id TEXT PRIMARY KEY,
                saved_at TEXT NOT NULL
            )
        """)


def save_analysis(resume_name, job_title, result, resume_text):
    breakdown = result.get("score_breakdown", {})
    actual_resume_skills = extract_skills(resume_text)
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO analyses (
                created_at, resume_name, job_title, overall_score,
                job_similarity, skill_coverage, keyword_coverage,
                resume_structure, matched_skills, missing_skills,
                recommendations, resume_skills
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            resume_name,
            job_title,
            float(result.get("overall_score", 0)),
            float(breakdown.get("Job Similarity", 0)),
            float(breakdown.get("Skill Coverage", 0)),
            float(breakdown.get("Keyword Coverage", 0)),
            float(breakdown.get("Resume Structure", 0)),
            json.dumps(result.get("matched_skills", [])),
            json.dumps(result.get("missing_skills", [])),
            json.dumps(result.get("recommendations", [])),
            json.dumps(actual_resume_skills),
        ))


def load_analyses(limit=100):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def save_interview(role, question, answer, score, feedback):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO interview_attempts
            (created_at, role, question, answer, score, feedback)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            role, question, answer, int(score), feedback
        ))


def load_interviews(limit=100):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM interview_attempts ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def is_job_saved(job_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT job_id FROM saved_jobs WHERE job_id = ?", (job_id,)
        ).fetchone()
    return row is not None


def toggle_saved_job(job_id):
    with get_connection() as conn:
        if is_job_saved(job_id):
            conn.execute("DELETE FROM saved_jobs WHERE job_id = ?", (job_id,))
        else:
            conn.execute(
                "INSERT OR IGNORE INTO saved_jobs(job_id, saved_at) VALUES (?, ?)",
                (job_id, datetime.now().isoformat(timespec="seconds"))
            )


init_db()


# ============================================================
# STYLING
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f8f7fc; color: #25212d; }
.block-container { max-width: 1500px; padding-top: 1.5rem; padding-bottom: 2.5rem; }
[data-testid="stSidebar"] { background: #fff; border-right: 1px solid #eeeaf5; }
[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }
.brand { font-size: 27px; font-weight: 800; color: #8847ee; margin-bottom: 25px; }
.brand span { color: #24202c; }
.nav-caption { color: #77717f; font-size: 12px; font-weight: 700; letter-spacing: 1px; margin: 18px 0 8px; }
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #fff; border: 1px solid #efedf3; border-radius: 17px;
    box-shadow: 0 4px 18px rgba(40,20,70,.035);
}
div.stButton > button { border-radius: 11px; min-height: 42px; font-weight: 600; }
div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg,#9c54ff,#7137e8); color: #fff; border: 0;
}
.metric-label { color: #81798c; font-size: 13px; }
.skill-chip { display:inline-block; background:#f2eaff; color:#8043d9; border:1px solid #e5d5ff; border-radius:9px; padding:7px 10px; margin:4px; font-size:12px; }
.missing-chip { display:inline-block; background:#fff8e4; color:#9b7415; border:1px solid #f3e5b7; border-radius:9px; padding:7px 10px; margin:4px; font-size:12px; }
.tip-item { background:#f3edff; border:1px solid #e8dcff; border-radius:10px; padding:11px 13px; margin:7px 0; color:#6840a8; font-size:13px; }
.status-good { background:#e7fbf2; border-radius:10px; padding:10px 12px; margin:7px 0; color:#16845b; font-size:13px; }
.status-warning { background:#fff9df; border-radius:10px; padding:10px 12px; margin:7px 0; color:#9a7410; font-size:13px; }
.job-meta { color:#77717f; font-size:13px; }
.small-note { color:#81798c; font-size:12px; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================
def safe_text(value):
    return html.escape(str(value))


def score_gauge(score, label="ATS Score"):
    fig = go.Figure(go.Pie(
        values=[score, max(0, 100 - score)],
        hole=.76,
        marker=dict(colors=["#9954f5", "#eeeaf3"], line=dict(color="white", width=2)),
        sort=False, direction="clockwise", textinfo="none", hoverinfo="skip"
    ))
    fig.update_layout(
        height=260, showlegend=False, margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{score:.0f}%</b><br><span style='font-size:13px'>{label}</span>",
            x=.5, y=.5, font=dict(size=34, color="#17131e"), showarrow=False
        )]
    )
    return fig


def render_chips(items, missing=False):
    css_class = "missing-chip" if missing else "skill-chip"
    prefix = "+ " if missing else ""
    if not items:
        st.caption("Nothing to display yet.")
        return
    chips = "".join(
        f'<span class="{css_class}">{prefix}{safe_text(item)}</span>'
        for item in items
    )
    st.markdown(chips, unsafe_allow_html=True)


def get_latest_analysis():
    rows = load_analyses(limit=1)
    return rows[0] if rows else None


def calculate_job_match(resume_skills, job_skills):
    job_set = set(job_skills)
    if not job_set:
        return 0, []
    matched = sorted(set(resume_skills).intersection(job_set))
    return round(len(matched) / len(job_set) * 100), matched


def evaluate_interview_answer(answer, keywords):
    answer_lower = answer.lower()
    matched = [word for word in keywords if word.lower() in answer_lower]
    score = round(len(matched) / max(len(keywords), 1) * 100)
    if len(answer.split()) < 12:
        feedback = "Your answer is quite short. Add a definition, explanation and a practical example."
    elif score >= 60:
        feedback = "Good coverage of the key concepts. Improve it further with a concrete example and clear structure."
    elif score >= 30:
        feedback = "You have some relevant points. Include more core terminology and explain how the concept works."
    else:
        feedback = "Revisit the concept and structure your response: define it, explain it, then give an example."
    return score, matched, feedback


def page_heading(title, subtitle):
    st.title(title)
    st.caption(subtitle)
    st.divider()


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown('<div class="brand">✦ <span>NeuroNexus</span></div>', unsafe_allow_html=True)
    st.text_input("🔍 Search", placeholder="Search dashboard", key="global_search")
    st.markdown('<div class="nav-caption">MAIN MENU</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["Dashboard", "Mock Interviews", "Resume Analyzer", "Jobs", "Progress", "Insights"],
        index=2,
        label_visibility="collapsed",
        key="current_page",
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:linear-gradient(145deg,#a45aff,#7136e8);
                border-radius:18px;padding:20px;color:white;text-align:center;">
        <div style="font-size:25px;">✦</div>
        <h3 style="color:white;margin:5px;">NeuroNexus AI</h3>
        <p style="font-size:12px;">Smart Career Assistant</p>
        <p style="font-size:12px;">Resume Analysis &amp; Job Matching</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("NeuroNexus NLP Project")
    st.caption("Traditional NLP • Team Project")


# ============================================================
# DASHBOARD
# ============================================================
if page == "Dashboard":
    page_heading("Dashboard", "Your career preparation overview.")
    latest = get_latest_analysis()
    analyses = load_analyses()
    interviews = load_interviews()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Resume analyses", len(analyses))
    c2.metric("Interview answers", len(interviews))
    c3.metric("Saved jobs", sum(is_job_saved(job["id"]) for job in JOBS))
    c4.metric("Latest ATS score", f"{latest['overall_score']:.0f}%" if latest else "—")

    left, right = st.columns([1.2, 1], gap="large")
    with left:
        with st.container(border=True):
            st.subheader("Welcome to NeuroNexus")
            st.write("Use the navigation menu to analyze a resume, practice interview questions, explore sample jobs and track your progress.")
            st.caption("Choose **Resume Analyzer** from the sidebar to start a new analysis.")
    with right:
        with st.container(border=True):
            st.subheader("Latest resume analysis")
            if latest:
                st.plotly_chart(score_gauge(latest["overall_score"]), use_container_width=True,
                                config={"displayModeBar": False})
                st.write(f"**Resume:** {latest['resume_name']}")
                st.write(f"**Compared against:** {latest['job_title']}")
                st.caption(f"Saved: {latest['created_at']}")
            else:
                st.info("No analysis saved yet. Visit Resume Analyzer to run your first analysis.")

    st.subheader("Recent activity")
    if analyses:
        activity = pd.DataFrame([{
            "Date": row["created_at"], "Resume": row["resume_name"],
            "Job target": row["job_title"], "ATS score": f"{row['overall_score']:.0f}%"
        } for row in analyses[:5]])
        st.dataframe(activity, use_container_width=True, hide_index=True)
    else:
        st.info("Your completed analyses will appear here.")


# ============================================================
# RESUME ANALYZER
# ============================================================
elif page == "Resume Analyzer":
    page_heading("Resume Analyzer", "Upload a PDF or DOCX resume and compare it with a target job description.")

    with st.expander("📄 Upload Resume & Job Description", expanded=True):
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"], key="resume_upload")
        job_title = st.text_input("Target job title", placeholder="e.g. Python Developer Intern")
        job_description = st.text_area("Paste Job Description", height=160, placeholder="Paste the full job description here...")
        if st.button("✦ Analyze My Resume", type="primary", use_container_width=True):
            if uploaded_file is None:
                st.error("Please upload your resume first.")
            elif not job_description.strip():
                st.error("Please paste a job description.")
            else:
                try:
                    with st.spinner("Extracting text and calculating your resume score..."):
                        resume_text = extract_resume_text(uploaded_file)
                        result = analyze_resume(resume_text, job_description)
                        save_analysis(
                            uploaded_file.name,
                            job_title.strip() or "Custom job description",
                            result,
                            resume_text
                        )
                        st.session_state.last_result = result
                        st.session_state.last_resume_text = resume_text
                        st.session_state.last_resume_name = uploaded_file.name
                    st.success("Resume analyzed and saved to Progress.")
                except Exception as exc:
                    st.error(f"Could not analyze this file: {exc}")

    result = st.session_state.get("last_result")
    if result:
        score = float(result.get("overall_score", 0))
        breakdown = result.get("score_breakdown", {})
        sections = result.get("sections", {})
        matched = result.get("matched_skills", [])
        missing = result.get("missing_skills", [])
        recommendations = result.get("recommendations", [])

        left, right = st.columns([1.05, 1.15], gap="large")
        with left:
            with st.container(border=True):
                st.subheader("ATS Analysis Score")
                st.plotly_chart(score_gauge(score), use_container_width=True,
                                config={"displayModeBar": False})
                st.markdown(f"### 📄 {safe_text(st.session_state.get('last_resume_name', 'Resume'))}")
                st.write("Your resume has been analyzed.")
                report = f"""NEURONEXUS RESUME ANALYSIS REPORT
Resume: {st.session_state.get('last_resume_name', '')}
Overall ATS score: {score:.0f}%
Score breakdown: {json.dumps(breakdown, indent=2)}
Matched skills: {', '.join(matched)}
Missing skills: {', '.join(missing)}
Section checks: {json.dumps(sections, indent=2)}
Recommendations:
""" + "\n".join(f"- {item}" for item in recommendations)
                st.download_button("⬇️ Download Report", report,
                                   file_name="NeuroNexus_Resume_Report.txt",
                                   mime="text/plain", use_container_width=True)
        with right:
            with st.container(border=True):
                st.subheader("Keyword Match")
                keyword_score = float(breakdown.get("Keyword Coverage", 0))
                st.write("🔎 Industry-relevant terms")
                st.progress(max(0, min(100, int(keyword_score))) / 100)
                st.caption(f"Keyword coverage: {keyword_score:.0f}%")
            with st.container(border=True):
                st.subheader("Formatting Feedback")
                for section_name, present in sections.items():
                    if present:
                        st.markdown(f'<div class="status-good">✓ &nbsp; {safe_text(section_name)} section detected</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="status-warning">⚠ &nbsp; Add a clear {safe_text(section_name)} section</div>', unsafe_allow_html=True)

        st.subheader("Skills Analysis")
        s1, s2 = st.columns(2, gap="large")
        with s1:
            with st.container(border=True):
                st.markdown("**Matched Skills**")
                render_chips(matched)
        with s2:
            with st.container(border=True):
                st.markdown("**Missing High-Value Keywords**")
                render_chips(missing, missing=True)

        st.subheader("Score Breakdown")
        with st.container(border=True):
            chart_df = pd.DataFrame({"Category": list(breakdown.keys()), "Score": list(breakdown.values())})
            fig = px.bar(chart_df, x="Score", y="Category", orientation="h", text="Score",
                         range_x=[0, 110], color_discrete_sequence=["#8546ed"])
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(height=260, margin=dict(l=10, r=35, t=10, b=10),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.subheader("Quick Tips")
        with st.container(border=True):
            for i, recommendation in enumerate(recommendations, 1):
                st.markdown(f'<div class="tip-item"><b>{i}.</b> {safe_text(recommendation)}</div>', unsafe_allow_html=True)

        with st.expander("View Extracted Resume Text"):
            st.text(st.session_state.get("last_resume_text", ""))
    else:
        st.info("Run an analysis above. Your result will appear here and be saved in Progress.")


# ============================================================
# MOCK INTERVIEWS
# ============================================================
elif page == "Mock Interviews":
    page_heading("Mock Interviews", "Practice role-specific technical questions and receive instant rule-based feedback.")
    role = st.selectbox("Choose an interview track", list(INTERVIEW_QUESTIONS.keys()))
    question_list = INTERVIEW_QUESTIONS[role]

    if "interview_question_index" not in st.session_state:
        st.session_state.interview_question_index = 0
    if "interview_role" not in st.session_state:
        st.session_state.interview_role = role
    if st.session_state.interview_role != role:
        st.session_state.interview_role = role
        st.session_state.interview_question_index = 0

    idx = st.session_state.interview_question_index % len(question_list)
    question = question_list[idx]["q"]
    with st.container(border=True):
        st.caption(f"{role} • Question {idx + 1} of {len(question_list)}")
        st.subheader(question)
        answer = st.text_area("Your answer", height=180, key=f"answer_{role}_{idx}",
                              placeholder="Write your answer in your own words...")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Submit answer", type="primary", use_container_width=True):
                if len(answer.split()) < 5:
                    st.warning("Please write a fuller answer (at least five words) before submitting.")
                else:
                    score, matched_terms, feedback = evaluate_interview_answer(answer, question_list[idx]["keywords"])
                    save_interview(role, question, answer, score, feedback)
                    st.session_state.interview_feedback = {
                        "score": score, "matched": matched_terms, "feedback": feedback
                    }
        with col_b:
            if st.button("Next question", use_container_width=True):
                st.session_state.interview_question_index = (idx + 1) % len(question_list)
                st.rerun()

    feedback = st.session_state.get("interview_feedback")
    if feedback:
        with st.container(border=True):
            st.subheader(f"Answer feedback: {feedback['score']}% keyword coverage")
            st.progress(feedback["score"] / 100)
            st.write(feedback["feedback"])
            st.write("**Relevant concepts detected:** " + (", ".join(feedback["matched"]) or "None detected"))
            st.caption("This is automated keyword-based practice feedback, not an expert human interview assessment.")

    st.subheader("Your recent practice")
    attempts = load_interviews(limit=10)
    if attempts:
        st.dataframe(pd.DataFrame([{
            "Date": x["created_at"], "Role": x["role"], "Score": f"{x['score']}%",
            "Question": x["question"]
        } for x in attempts]), use_container_width=True, hide_index=True)
    else:
        st.info("Your submitted practice answers will be saved here.")


# ============================================================
# JOBS
# ============================================================
elif page == "Jobs":
    page_heading("Jobs", "Search and save curated sample opportunities. These are demo listings, not live vacancies.")
    latest = get_latest_analysis()
    resume_skills = []
    if latest:
        try:
            resume_skills = json.loads(latest.get("resume_skills", "[]"))
        except Exception:
            resume_skills = []

    search = st.text_input("Search jobs", placeholder="Search by title, company, skill or location")
    type_filter = st.selectbox("Employment type", ["All", "Internship", "Trainee", "Full-time"])
    location_filter = st.selectbox("Location", ["All", "Gurugram, Haryana", "Delhi NCR", "Remote (India)", "Noida, Uttar Pradesh"])

    filtered = []
    for job in JOBS:
        haystack = " ".join([job["title"], job["company"], job["location"], job["description"], *job["skills"]]).lower()
        if search.lower() not in haystack:
            continue
        if type_filter != "All" and job["type"] != type_filter:
            continue
        if location_filter != "All" and job["location"] != location_filter:
            continue
        filtered.append(job)

    st.caption(f"{len(filtered)} sample listing(s) found • Demo data for project presentation")
    if not latest:
        st.info("Run Resume Analyzer first to calculate skill matches against these listings.")
    for job in filtered:
        match_score, matched_terms = calculate_job_match(resume_skills, job["skills"])
        with st.container(border=True):
            top_l, top_r = st.columns([4, 1])
            with top_l:
                st.subheader(job["title"])
                st.markdown(f"**{job['company']}**  ·  {job['location']}")
                st.caption(f"{job['type']} • {job['level']} • Demo listing ID: {job['id']}")
            with top_r:
                st.metric("Skill match", f"{match_score}%")
            st.write(job["description"])
            st.markdown("**Skills:**")
            render_chips(job["skills"])
            if matched_terms:
                st.caption("Skills matched with your latest resume analysis: " + ", ".join(matched_terms))
            save_label = "★ Saved" if is_job_saved(job["id"]) else "☆ Save job"
            if st.button(save_label, key=f"save_{job['id']}"):
                toggle_saved_job(job["id"])
                st.rerun()


# ============================================================
# PROGRESS
# ============================================================
elif page == "Progress":
    page_heading("Progress", "Your saved resume analyses and interview practice history.")
    analyses = load_analyses()
    attempts = load_interviews()
    if analyses:
        scores = [row["overall_score"] for row in analyses]
        c1, c2, c3 = st.columns(3)
        c1.metric("Analyses completed", len(analyses))
        c2.metric("Latest ATS score", f"{scores[0]:.0f}%")
        c3.metric("Best ATS score", f"{max(scores):.0f}%")

        st.subheader("ATS score over time")
        ordered = list(reversed(analyses))
        trend = pd.DataFrame({
            "Analysis": list(range(1, len(ordered) + 1)),
            "ATS score": [row["overall_score"] for row in ordered],
            "Resume": [row["resume_name"] for row in ordered],
        })
        with st.container(border=True):
            fig = px.line(trend, x="Analysis", y="ATS score", markers=True,
                          hover_data=["Resume"], range_y=[0, 100],
                          color_discrete_sequence=["#8546ed"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.subheader("Analysis history")
        st.dataframe(pd.DataFrame([{
            "Date": x["created_at"], "Resume": x["resume_name"],
            "Job target": x["job_title"], "ATS score": f"{x['overall_score']:.0f}%"
        } for x in analyses]), use_container_width=True, hide_index=True)
    else:
        st.info("No resume analyses saved yet. Complete an analysis to start tracking your progress.")

    st.subheader("Interview practice history")
    if attempts:
        st.dataframe(pd.DataFrame([{
            "Date": x["created_at"], "Role": x["role"],
            "Score": f"{x['score']}%", "Question": x["question"]
        } for x in attempts]), use_container_width=True, hide_index=True)
    else:
        st.info("No interview answers saved yet.")


# ============================================================
# INSIGHTS
# ============================================================
elif page == "Insights":
    page_heading("Insights", "Understand skill gaps and identify what to improve next.")
    latest = get_latest_analysis()
    analyses = load_analyses()
    if not latest:
        st.info("Complete a resume analysis first. Insights will be generated from your saved analysis.")
    else:
        matched = json.loads(latest["matched_skills"])
        missing = json.loads(latest["missing_skills"])
        breakdown = {
            "Job Similarity": latest["job_similarity"],
            "Skill Coverage": latest["skill_coverage"],
            "Keyword Coverage": latest["keyword_coverage"],
            "Resume Structure": latest["resume_structure"],
        }

        c1, c2 = st.columns(2, gap="large")
        with c1:
            with st.container(border=True):
                st.subheader("Strongest area")
                strongest = max(breakdown, key=breakdown.get)
                st.metric(strongest, f"{breakdown[strongest]:.0f}%")
                st.caption("Based on your latest saved resume analysis.")
        with c2:
            with st.container(border=True):
                st.subheader("Area to improve")
                weakest = min(breakdown, key=breakdown.get)
                st.metric(weakest, f"{breakdown[weakest]:.0f}%")
                st.caption("Focus your next revision on this score component.")

        st.subheader("Score component comparison")
        with st.container(border=True):
            chart_df = pd.DataFrame({"Component": list(breakdown.keys()), "Score": list(breakdown.values())})
            fig = px.bar(chart_df, x="Component", y="Score", range_y=[0, 100],
                         color_discrete_sequence=["#8546ed"], text="Score")
            fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        skill_l, skill_r = st.columns(2, gap="large")
        with skill_l:
            with st.container(border=True):
                st.subheader("Skills matched")
                render_chips(matched)
        with skill_r:
            with st.container(border=True):
                st.subheader("Skills to work on")
                render_chips(missing, missing=True)

        if analyses and len(analyses) > 1:
            st.subheader("Score change")
            old_score = analyses[1]["overall_score"]
            latest_score = latest["overall_score"]
            delta = latest_score - old_score
            st.metric("Change vs previous analysis", f"{delta:+.0f} points",
                      delta=f"{delta:+.0f} points")
        st.caption("Insights are calculated from the local TF-IDF/skill-matching analysis; they are guidance, not a hiring decision.")


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown(
    "<div style='text-align:center;color:#999;font-size:12px;'>"
    "© 2026 NeuroNexus | Traditional NLP Career Assistant | Local demo application"
    "</div>",
    unsafe_allow_html=True,
)
