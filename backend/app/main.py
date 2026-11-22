
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers.resume import router as resume_router

app = FastAPI(
    title="NeuroNexus AI API",
    description="AI-powered Resume Analysis Platform",
    version="1.0.0"
)

# Allow local and deployed frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://neuro-nexus-nlp-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(resume_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to NeuroNexus AI",
        "status": "Backend is running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "project": "NeuroNexus AI",
        "version": "1.0.0"
    }
