
import streamlit as st
import plotly.express as px

from transformer_analyzer import (
    extract_resume_text,
    analyze_resume
)

st.set_page_config(
    page_title="NeuroNexus Transformer Resume Analyzer",
    page_icon="✨",
    layout="wide"
)

st.title("✨ NeuroNexus")
st.header("Transformer-Based Resume Analyzer")

st.write(
    "Analyze resumes using Transformer-based semantic "
    "similarity and skill matching."
)

st.divider()

uploaded_file = st.file_uploader(
    "Upload your Resume",
    type=["pdf", "docx"]
)

job_title = st.text_input(
    "Target Job Title",
    placeholder="e.g. Machine Learning Engineer"
)

job_description = st.text_area(
    "Paste Job Description",
    height=200,
    placeholder="Paste the complete job description here..."
)

if st.button("Analyze Resume", type="primary"):

    if uploaded_file is None:
        st.error("Please upload a resume.")

    elif not job_description.strip():
        st.error("Please enter a job description.")

    else:
        try:
            with st.spinner(
                "Analyzing resume using Transformer AI..."
            ):
                resume_text = extract_resume_text(uploaded_file)

                if not resume_text.strip():
                    st.error("Could not extract text from this resume.")
                else:
                    result = analyze_resume(
                        resume_text,
                        job_description
                    )

                    st.success("Resume analysis completed!")

                    st.subheader(
                        f"Results for {job_title or 'Target Job'}"
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Overall Resume Score",
                        f"{result['overall_score']}%"
                    )

                    col2.metric(
                        "Semantic Similarity",
                        f"{result['similarity_score']}%"
                    )

                    col3.metric(
                        "Skill Match",
                        f"{result['skill_score']}%"
                    )

                    st.divider()

                    st.subheader("Score Visualization")

                    chart_data = {
                        "Metric": [
                            "Semantic Similarity",
                            "Skill Match"
                        ],
                        "Score": [
                            result["similarity_score"],
                            result["skill_score"]
                        ]
                    }

                    fig = px.bar(
                        chart_data,
                        x="Metric",
                        y="Score",
                        range_y=[0, 100],
                        text="Score",
                        title="Transformer Analysis Results"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Matched Skills")

                        if result["matched_skills"]:
                            for skill in result["matched_skills"]:
                                st.success(f"✓ {skill}")
                        else:
                            st.info("No matching skills found.")

                    with col2:
                        st.subheader("Missing Skills")

                        if result["missing_skills"]:
                            for skill in result["missing_skills"]:
                                st.warning(f"• {skill}")
                        else:
                            st.success("No missing listed skills.")

                    st.divider()

                    st.subheader("AI Recommendations")

                    for recommendation in result["recommendations"]:
                        st.info(recommendation)

                    report = f"""
NEURONEXUS - TRANSFORMER RESUME ANALYSIS

Job Title: {job_title}

Overall Score: {result['overall_score']}%
Semantic Similarity: {result['similarity_score']}%
Skill Match: {result['skill_score']}%

Matched Skills:
{', '.join(result['matched_skills'])}

Missing Skills:
{', '.join(result['missing_skills'])}

Recommendations:
{chr(10).join(result['recommendations'])}
"""

                    st.download_button(
                        "Download Analysis Report",
                        data=report,
                        file_name="Transformer_Resume_Report.txt",
                        mime="text/plain"
                    )

        except Exception as e:
            st.error(f"Analysis failed: {e}")

st.divider()

st.caption(
    "NeuroNexus | NLP Academic Project | "
    "Transformer-Based Semantic Resume Analysis"
)
