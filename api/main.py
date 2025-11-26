from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
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
from apps.analyzer.models import AnalysisSession, QualifiedCandidate
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
    If match percentage > 80%, automatically saves to QualifiedCandidate model
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
        
        # Check if candidate qualifies (>80%)
        is_qualified = False
        if float(session.match_percentage) > 80.0:
            is_qualified = True
            # Save to QualifiedCandidate model
            qualified_candidate = QualifiedCandidate.objects.create(
                analysis_session=session,
                resume_text=session.resume_text,
                job_description=session.job_description,
                match_percentage=session.match_percentage,
                matching_skills=session.matching_skills,
                matching_education=session.matching_education,
                matching_experience=session.matching_experience,
                highlighted_strengths=session.highlighted_strengths,
                identified_gaps=session.identified_gaps
            )
            logger.info(f"✅ Qualified candidate saved: {qualified_candidate.id} with {session.match_percentage}% match")
        
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
            processing_time=session.processing_time,
            is_qualified=is_qualified
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


@app.get("/api/fastapi/qualified-candidates")
async def list_qualified_candidates(
    status: Optional[str] = Query(None, description="Filter by status"),
    min_percentage: float = Query(80.0, description="Minimum match percentage"),
    highly_qualified: bool = Query(False, description="Filter for >90% match")
):
    """
    List all qualified candidates (>80% match)
    
    Query parameters:
        - status: Filter by status (NEW, REVIEWED, CONTACTED, etc.)
        - min_percentage: Minimum match percentage (default: 80)
        - highly_qualified: Filter for >90% match
    """
    queryset = QualifiedCandidate.objects.all()
    
    # Apply filters
    if status:
        queryset = queryset.filter(status=status.upper())
    
    queryset = queryset.filter(match_percentage__gte=min_percentage)
    
    if highly_qualified:
        queryset = queryset.filter(match_percentage__gte=90.0)
    
    candidates = queryset[:50]  # Limit to 50 results
    
    return [
        {
            "id": str(c.id),
            "match_percentage": float(c.match_percentage),
            "matching_skills": c.matching_skills,
            "matching_education": c.matching_education,
            "matching_experience": c.matching_experience,
            "highlighted_strengths": c.highlighted_strengths,
            "identified_gaps": c.identified_gaps,
            "status": c.status,
            "is_contacted": c.is_contacted,
            "qualification_date": c.qualification_date.isoformat(),
            "is_highly_qualified": c.is_highly_qualified
        }
        for c in candidates
    ]


@app.get("/api/fastapi/qualified-candidates/{candidate_id}")
async def get_qualified_candidate(candidate_id: str):
    """Retrieve qualified candidate by ID"""
    try:
        candidate = QualifiedCandidate.objects.get(id=candidate_id)
        return {
            "id": str(candidate.id),
            "analysis_session_id": str(candidate.analysis_session.id),
            "match_percentage": float(candidate.match_percentage),
            "matching_skills": candidate.matching_skills,
            "matching_education": candidate.matching_education,
            "matching_experience": candidate.matching_experience,
            "highlighted_strengths": candidate.highlighted_strengths,
            "identified_gaps": candidate.identified_gaps,
            "status": candidate.status,
            "is_contacted": candidate.is_contacted,
            "notes": candidate.notes,
            "qualification_date": candidate.qualification_date.isoformat(),
            "is_highly_qualified": candidate.is_highly_qualified
        }
    except QualifiedCandidate.DoesNotExist:
        raise HTTPException(status_code=404, detail="Qualified candidate not found")


@app.patch("/api/fastapi/qualified-candidates/{candidate_id}")
async def update_qualified_candidate(
    candidate_id: str,
    status: Optional[str] = Form(None),
    is_contacted: Optional[bool] = Form(None),
    notes: Optional[str] = Form(None)
):
    """
    Update qualified candidate details
    
    Form data:
        - status: string (NEW, REVIEWED, CONTACTED, INTERVIEWING, HIRED, REJECTED)
        - is_contacted: boolean
        - notes: string
    """
    try:
        candidate = QualifiedCandidate.objects.get(id=candidate_id)
        
        if status is not None:
            candidate.status = status.upper()
        if is_contacted is not None:
            candidate.is_contacted = is_contacted
        if notes is not None:
            candidate.notes = notes
        
        candidate.save()
        
        return {
            "id": str(candidate.id),
            "status": candidate.status,
            "is_contacted": candidate.is_contacted,
            "notes": candidate.notes,
            "message": "Candidate updated successfully"
        }
        
    except QualifiedCandidate.DoesNotExist:
        raise HTTPException(status_code=404, detail="Qualified candidate not found")


@app.get("/api/fastapi/qualified-candidates-stats")
async def qualified_candidates_stats():
    """Get statistics about qualified candidates"""
    total_qualified = QualifiedCandidate.objects.count()
    highly_qualified = QualifiedCandidate.objects.filter(match_percentage__gte=90.0).count()
    
    status_breakdown = {}
    for status_choice in QualifiedCandidate.STATUS_CHOICES:
        status_code = status_choice[0]
        count = QualifiedCandidate.objects.filter(status=status_code).count()
        status_breakdown[status_code] = count
    
    return {
        "total_qualified_candidates": total_qualified,
        "highly_qualified_count": highly_qualified,
        "status_breakdown": status_breakdown,
        "contacted_count": QualifiedCandidate.objects.filter(is_contacted=True).count(),
        "not_contacted_count": QualifiedCandidate.objects.filter(is_contacted=False).count()
    }