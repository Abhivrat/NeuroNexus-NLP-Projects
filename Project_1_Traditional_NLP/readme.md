NeuroNexus — Functional Traditional NLP Career Assistant
Features
- Dashboard with saved activity and latest ATS score
- Resume Analyzer for PDF/DOCX using the supplied TF-IDF/skill-matching analyzer
- Mock Interviews with role-based questions, answer submission, keyword-based feedback and saved attempts
- Jobs page with searchable/filterable sample listings and saved jobs
- Progress page with SQLite-persisted analysis and interview history
- Insights page with score breakdown and skill-gap charts
Important data note
The Jobs page uses curated local demo listings. They are sample records for demonstration, not live vacancies. Mock interview feedback is automated and keyword-based, not an expert human assessment.
Setup (Windows PowerShell)
Open this folder in VS Code, then run:
py -3.10 -m venv venv
.env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
If PowerShell blocks activation, for the current terminal session run:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.env\Scripts\Activate.ps1
If the streamlit.exe launcher is blocked by Application Control, use:
python -m streamlit run app.py
Then open http://localhost:8501.
Data storage
A local neuronexus.db SQLite database is created automatically beside app.py. It stores resume analysis history, mock interview attempts and saved job IDs. Keep this file if you want to retain demo history.
Notes
- analyzer.py is the original Traditional NLP analysis module and is included unchanged.
- The application is a local college-project demo. It does not create user accounts, submit job applications, connect to employers, or fetch liv