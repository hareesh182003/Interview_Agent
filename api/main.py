from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pathlib import Path

# Add Django project to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ats_analyzer.settings')
import django
django.setup()

# Import Django models and services after setup
from apps.analyzer.models import AnalysisSession
from apps.analyzer.services.pdf_extractor import PDFExtractor
from apps.analyzer.services.ai_analyzer import AIAnalyzer
from api.schemas.response import AnalysisResponse
import time
import tempfile
import logging

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="ATS Analyzer API",
    description="AI-powered Resume and Job Description Analysis",
    version="1.0.0",
    docs_url="/api/fastapi/docs",
    openapi_url="/api/fastapi/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/fastapi/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "fastapi"}


@app.post("/api/fastapi/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume_file: UploadFile = File(..., description="PDF resume file"),
    job_description: str = Form(..., description="Job description text")
):
    """
    Analyze resume against job description using AI
    
    - **resume_file**: PDF file of candidate's resume (max 5MB)
    - **job_description**: Text of the job description
    
    Returns detailed match analysis with percentage score
    """
    start_time = time.time()
    
    # Validate file
    if not resume_file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await resume_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Extract text from PDF
        logger.info(f"Extracting text from {resume_file.filename}")
        resume_text = PDFExtractor.extract_text(tmp_path)
        
        # Analyze with AI
        logger.info("Starting AI analysis")
        analyzer = AIAnalyzer()
        analysis_result = analyzer.analyze_resume_match(resume_text, job_description)
        
        # Save to Django database
        session = AnalysisSession.objects.create(
            job_description=job_description,
            resume_text=resume_text,
            match_percentage=analysis_result['match_percentage'],
            matching_skills=analysis_result['matching_skills'],
            matching_education=analysis_result['matching_education'],
            matching_experience=analysis_result['matching_experience'],
            highlighted_strengths=analysis_result['highlighted_strengths'],
            identified_gaps=analysis_result['identified_gaps'],
            ai_response=analysis_result['raw_response'],
            processing_time=time.time() - start_time
        )
        
        # Clean up
        os.unlink(tmp_path)
        
        return AnalysisResponse(
            session_id=str(session.id),
            match_percentage=float(session.match_percentage),
            matching_skills=session.matching_skills,
            matching_education=session.matching_education,
            matching_experience=session.matching_experience,
            highlighted_strengths=session.highlighted_strengths,
            identified_gaps=session.identified_gaps,
            processing_time=session.processing_time
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/fastapi/analysis/{session_id}")
async def get_analysis(session_id: str):
    """Retrieve analysis by session ID"""
    try:
        session = AnalysisSession.objects.get(id=session_id)
        return {
            "session_id": str(session.id),
            "match_percentage": float(session.match_percentage),
            "matching_skills": session.matching_skills,
            "matching_education": session.matching_education,
            "matching_experience": session.matching_experience,
            "highlighted_strengths": session.highlighted_strengths,
            "identified_gaps": session.identified_gaps,
            "created_at": session.created_at.isoformat(),
            "processing_time": session.processing_time
        }
    except AnalysisSession.DoesNotExist:
        raise HTTPException(status_code=404, detail="Analysis session not found")


@app.get("/api/fastapi/analyses")
async def list_analyses(limit: int = 10):
    """List recent analysis sessions"""
    sessions = AnalysisSession.objects.all()[:limit]
    return [
        {
            "session_id": str(s.id),
            "match_percentage": float(s.match_percentage),
            "created_at": s.created_at.isoformat()
        }
        for s in sessions
    ]