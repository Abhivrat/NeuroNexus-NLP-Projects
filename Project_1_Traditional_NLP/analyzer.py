
import re
import io
import pymupdf
from docx import Document

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# 1. Technical skills database
SKILLS = [
    "python", "java", "c++", "c", "sql", "mysql", "mongodb",
    "machine learning", "deep learning", "natural language processing",
    "nlp", "tensorflow", "pytorch", "scikit-learn",
    "pandas", "numpy", "opencv", "computer vision",
    "data analysis", "data science", "data visualization",
    "power bi", "tableau", "excel", "flask", "django",
    "react", "javascript", "html", "css", "git", "github",
    "docker", "aws", "azure", "linux", "rest api",
    "communication", "leadership", "teamwork",
    "problem solving", "project management"
]


# 2. Extract text from PDF or DOCX
def extract_resume_text(uploaded_file):

    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if filename.endswith(".pdf"):

        pdf = pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        )

        text = ""

        for page in pdf:
            text += page.get_text() + "\n"

        pdf.close()

        return text

    elif filename.endswith(".docx"):

        document = Document(
            io.BytesIO(file_bytes)
        )

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

        return text

    else:
        raise ValueError("Only PDF and DOCX files are supported.")


# 3. Text preprocessing
def preprocess_text(text):

    text = text.lower()

    text = re.sub(
        r'\S+@\S+',
        ' ',
        text
    )

    text = re.sub(
        r'https?://\S+|www\.\S+',
        ' ',
        text
    )

    text = re.sub(
        r'[^a-z0-9+#.\s]',
        ' ',
        text
    )

    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    return text.strip()


# 4. Extract skills from resume or job description
def extract_skills(text):

    text = preprocess_text(text)

    found_skills = []

    for skill in SKILLS:

        pattern = (
            r'(?<![a-z0-9])'
            + re.escape(skill)
            + r'(?![a-z0-9])'
        )

        if re.search(pattern, text):

            found_skills.append(skill)

    return sorted(set(found_skills))


# 5. Calculate TF-IDF cosine similarity
def calculate_similarity(resume_text, job_description):

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000
    )

    documents = [
        preprocess_text(resume_text),
        preprocess_text(job_description)
    ]

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    return float(similarity)


# 6. Check important resume sections
def check_resume_sections(text):

    text = preprocess_text(text)

    sections = {

        "Education": [
            "education",
            "university",
            "college",
            "bachelor"
        ],

        "Experience": [
            "experience",
            "internship",
            "employment",
            "work history"
        ],

        "Projects": [
            "projects",
            "project"
        ],

        "Skills": [
            "skills",
            "technical skills"
        ],

        "Contact Information": [
            "linkedin",
            "github",
            "email",
            "phone"
        ]
    }

    results = {}

    for section, keywords in sections.items():

        results[section] = any(
            keyword in text
            for keyword in keywords
        )

    return results


# 7. Calculate keyword coverage
def keyword_coverage(resume_text, job_description):

    resume_words = set(
        re.findall(
            r'\b[a-z][a-z0-9+#.]*\b',
            preprocess_text(resume_text)
        )
    )

    job_words = set(
        re.findall(
            r'\b[a-z][a-z0-9+#.]*\b',
            preprocess_text(job_description)
        )
    )

    stop_words = set(TfidfVectorizer(
        stop_words="english"
    ).get_stop_words())

    job_words = job_words - stop_words

    if not job_words:
        return 0.0

    matched = resume_words.intersection(job_words)

    return len(matched) / len(job_words)


# 8. Generate improvement recommendations
def generate_recommendations(
    resume_text,
    missing_skills,
    sections,
    similarity
):

    recommendations = []

    if missing_skills:

        recommendations.append(
            "Consider adding evidence of these job-related skills "
            "if you genuinely possess them: "
            + ", ".join(missing_skills)
        )

    for section, present in sections.items():

        if not present:

            recommendations.append(
                f"Add a clear {section} section to your resume."
            )

    if similarity < 0.30:

        recommendations.append(
            "Improve alignment between your resume and the job description."
        )

    if len(resume_text.split()) < 150:

        recommendations.append(
            "Your resume appears short. Add relevant projects, "
            "experience and achievements."
        )

    recommendations.append(
        "Use action verbs and measurable achievements "
        "to describe your work."
    )

    recommendations.append(
        "Keep formatting consistent and avoid spelling mistakes."
    )

    return recommendations


# 9. Main resume analysis function
def analyze_resume(resume_text, job_description):

    similarity = calculate_similarity(
        resume_text,
        job_description
    )

    resume_skills = set(
        extract_skills(resume_text)
    )

    job_skills = set(
        extract_skills(job_description)
    )

    matched_skills = sorted(
        resume_skills.intersection(job_skills)
    )

    missing_skills = sorted(
        job_skills - resume_skills
    )

    skill_score = (
        len(matched_skills) / len(job_skills)
        if job_skills else 0
    )

    sections = check_resume_sections(resume_text)

    structure_score = (
        sum(sections.values()) / len(sections)
    )

    keyword_score = keyword_coverage(
        resume_text,
        job_description
    )

    score_breakdown = {

        "Job Similarity": round(similarity * 100),

        "Skill Coverage": round(skill_score * 100),

        "Keyword Coverage": round(keyword_score * 100),

        "Resume Structure": round(structure_score * 100)
    }

    final_score = (

        similarity * 35
        + skill_score * 35
        + keyword_score * 15
        + structure_score * 15

    )

    recommendations = generate_recommendations(
        resume_text,
        missing_skills,
        sections,
        similarity
    )

    return {

        "overall_score": round(final_score),

        "score_breakdown": score_breakdown,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "sections": sections,

        "recommendations": recommendations,

        "similarity": round(similarity * 100, 2)
    }
