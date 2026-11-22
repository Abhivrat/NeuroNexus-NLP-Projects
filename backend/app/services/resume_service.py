
import re
from pathlib import Path

import pymupdf
from docx import Document
from sentence_transformers import SentenceTransformer, util


# Load the Transformer model only when needed
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = None


def get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def extract_resume_text(file_path: str) -> str:
    """Extract text from PDF or DOCX resumes."""

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
    "python", "java", "c++", "sql", "machine learning",
    "deep learning", "nlp", "natural language processing",
    "tensorflow", "pytorch", "scikit-learn", "docker",
    "git", "flask", "django", "fastapi", "react",
    "mongodb", "aws", "data analysis", "excel",
    "communication", "problem solving", "rest api"
]


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """Analyze resume using Transformer embeddings and skill matching."""

    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)

    if not resume_text or not job_description:
        raise ValueError("Resume and job description cannot be empty.")

    model = get_model()

    # Transformer semantic similarity
    embeddings = model.encode(
        [resume_text, job_description],
        convert_to_tensor=True
    )

    similarity = util.cos_sim(
        embeddings[0],
        embeddings[1]
    ).item()

    semantic_score = round(max(0, min(100, similarity * 100)), 2)

    # Skill matching
    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    required_skills = [
        skill for skill in SKILLS if skill in job_lower
    ]

    matched_skills = [
        skill for skill in required_skills if skill in resume_lower
    ]

    missing_skills = [
        skill for skill in required_skills if skill not in resume_lower
    ]

    skill_score = (
        round(len(matched_skills) / len(required_skills) * 100, 2)
        if required_skills else 0
    )

    overall_score = round(
        (semantic_score * 0.60) + (skill_score * 0.40), 2
    )

    recommendations = []

    if missing_skills:
        recommendations.append(
            "Review the missing job-related skills and add them "
            "only if you genuinely possess them."
        )

    if semantic_score < 50:
        recommendations.append(
            "Improve alignment between your experience and the job description."
        )

    if skill_score < 60:
        recommendations.append(
            "Highlight relevant technical skills and project experience."
        )

    if not recommendations:
        recommendations.append(
            "Good alignment. Continue improving your achievements "
            "with measurable results."
        )

    return {
        "overall_score": overall_score,
        "semantic_similarity": semantic_score,
        "skill_match": skill_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "required_skills": required_skills,
        "recommendations": recommendations
    }
