
import re
from pathlib import Path

import pymupdf
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Extract text from PDF or DOCX
def extract_resume_text(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        with pymupdf.open(file_path) as pdf:
            text = "\n".join(page.get_text() for page in pdf)

    elif extension == ".docx":
        document = Document(file_path)
        text = "\n".join(
            paragraph.text for paragraph in document.paragraphs
        )

    else:
        raise ValueError("Only PDF and DOCX files are supported.")

    if not text.strip():
        raise ValueError("No readable text found in the resume.")

    return text


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


SKILLS = [
    "python", "java", "c++", "sql",
    "machine learning", "deep learning",
    "nlp", "natural language processing",
    "tensorflow", "pytorch", "scikit-learn",
    "docker", "git", "flask", "django",
    "fastapi", "react", "mongodb", "aws",
    "data analysis", "excel", "communication",
    "problem solving", "rest api",
    "html", "css", "javascript",
    "data structures", "algorithms",
    "opencv", "pandas", "numpy",
    "power bi", "tableau"
]


def find_skills(text: str) -> list:
    text = text.lower()
    matched = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            matched.append(skill)

    return matched


def analyze_resume(resume_text: str, job_description: str) -> dict:
    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)

    if not resume_text or not job_description:
        raise ValueError("Resume and job description cannot be empty.")

    # Limit text size to keep memory usage low
    resume_text = resume_text[:20000]
    job_description = job_description[:20000]

    # Lightweight NLP: TF-IDF and cosine similarity
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=12000,
        sublinear_tf=True
    )

    try:
        vectors = vectorizer.fit_transform([
            resume_text,
            job_description
        ])

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        text_score = round(float(similarity) * 100, 2)

    except ValueError:
        text_score = 0.0

    # Skill matching
    required_skills = find_skills(job_description)
    resume_skills = find_skills(resume_text)

    matched_skills = [
        skill for skill in required_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in resume_skills
    ]

    skill_score = (
        round(
            len(matched_skills) / len(required_skills) * 100,
            2
        )
        if required_skills else 0.0
    )

    # Overall score
    overall_score = round(
        (text_score * 0.60) + (skill_score * 0.40),
        2
    )

    # Recommendations
    recommendations = []

    if missing_skills:
        recommendations.append(
            "Review missing job-related skills and add them "
            "only if you genuinely possess them."
        )

    if text_score < 50:
        recommendations.append(
            "Improve alignment between your resume experience "
            "and the job description."
        )

    if skill_score < 60:
        recommendations.append(
            "Highlight relevant technical skills and project experience."
        )

    if not recommendations:
        recommendations.append(
            "Good alignment. Improve your achievements with "
            "measurable results."
        )

    return {
        "overall_score": overall_score,
        "semantic_similarity": text_score,
        "skill_match": skill_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "required_skills": required_skills,
        "recommendations": recommendations
    }
