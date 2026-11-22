
import re
import pymupdf
from docx import Document
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load pretrained Transformer model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

SKILLS = [
    "python", "java", "c++", "machine learning",
    "deep learning", "nlp", "sql", "mongodb",
    "flask", "django", "react", "tensorflow",
    "pytorch", "scikit-learn", "docker", "aws",
    "communication", "data analysis", "excel",
    "power bi", "git", "rest api"
]


def extract_resume_text(uploaded_file):
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        with pymupdf.open(
            stream=uploaded_file.getvalue(),
            filetype="pdf"
        ) as pdf:
            return "\n".join(page.get_text() for page in pdf)

    elif filename.endswith(".docx"):
        document = Document(uploaded_file)
        return "\n".join(p.text for p in document.paragraphs)

    raise ValueError("Please upload a PDF or DOCX file.")


def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills(text):
    text = clean_text(text)
    return [skill for skill in SKILLS if skill in text]


def analyze_resume(resume_text, job_description):

    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_description)

    # Generate Transformer embeddings
    embeddings = model.encode(
        [resume_clean, job_clean],
        convert_to_numpy=True
    )

    # Semantic similarity
    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    similarity_score = round(float(similarity) * 100, 2)

    resume_skills = extract_skills(resume_clean)
    job_skills = extract_skills(job_clean)

    matched = sorted(set(resume_skills) & set(job_skills))
    missing = sorted(set(job_skills) - set(resume_skills))

    if job_skills:
        skill_score = round(
            len(matched) / len(job_skills) * 100, 2
        )
    else:
        skill_score = 0

    # Weighted overall score
    overall_score = round(
        similarity_score * 0.70 +
        skill_score * 0.30,
        2
    )

    recommendations = []

    if missing:
        recommendations.append(
            "Consider adding relevant missing skills "
            "if you genuinely possess them: " + ", ".join(missing)
        )

    if similarity_score < 50:
        recommendations.append(
            "Improve the alignment between your resume "
            "experience and the target job description."
        )

    if not recommendations:
        recommendations.append(
            "Good alignment! Continue improving your "
            "resume with measurable achievements."
        )

    return {
        "overall_score": overall_score,
        "similarity_score": similarity_score,
        "skill_score": skill_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendations": recommendations
    }
