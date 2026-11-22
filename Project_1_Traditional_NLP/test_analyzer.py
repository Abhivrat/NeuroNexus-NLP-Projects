
from analyzer import analyze_resume

resume = """
Abhivrat Pathak
B.Tech Computer Science Engineering

Skills:
Python, Java, Machine Learning, SQL,
Pandas, NumPy, Flask, HTML, CSS.

Projects:
AI Resume Analyzer
Developed a resume analysis system using Python.

Education:
Bachelor of Technology in Computer Science.

Experience:
Software Development Intern.
"""

job_description = """
We are looking for a Python Developer.

Required skills:
Python, SQL, Machine Learning, Flask,
Docker, AWS, REST API.

Candidate should have problem solving
and communication skills.
"""

result = analyze_resume(
    resume,
    job_description
)

print("\n===== RESUME ANALYSIS =====")

print("Overall Score:", result["overall_score"])

print("\nScore Breakdown:")
for key, value in result["score_breakdown"].items():
    print(key, ":", value)

print("\nMatched Skills:")
print(result["matched_skills"])

print("\nMissing Skills:")
print(result["missing_skills"])

print("\nRecommendations:")
for recommendation in result["recommendations"]:
    print("-", recommendation)
