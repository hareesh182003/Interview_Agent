from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import time
import logging

from .models import AnalysisSession, QualifiedCandidate
from .serializers import (
    AnalysisRequestSerializer,
    AnalysisResponseSerializer,
    AnalysisSessionSerializer,
    QualifiedCandidateSerializer,
    QualifiedCandidateListSerializer
)
from .services.pdf_extractor import PDFExtractor
from .services.ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)


@api_view(['POST'])
def analyze_resume(request):
    """
    Analyze resume against job description
    
    POST /api/django/analyze/
    
    Form data:
        - resume_file: PDF file
        - job_description: text
    
    Returns:
        - session_id: UUID
        - match_percentage: float
        - matching_skills: list
        - matching_education: string
        - matching_experience: string
        - highlighted_strengths: list
        - identified_gaps: list
        - processing_time: float
        - is_qualified: boolean (True if >80%)
    """
    start_time = time.time()
    
    # Validate request
    serializer = AnalysisRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    resume_file = serializer.validated_data['resume_file']
    job_description = serializer.validated_data['job_description']
    
    try:
        # Save file temporarily
        file_path = default_storage.save(f'temp/{resume_file.name}', resume_file)
        full_path = default_storage.path(file_path)
        
        # Extract text from PDF
        logger.info(f"Extracting text from {resume_file.name}")
        resume_text = PDFExtractor.extract_text(full_path)
        
        # Analyze with AI
        logger.info("Starting AI analysis")
        analyzer = AIAnalyzer()
        analysis_result = analyzer.analyze_resume_match(resume_text, job_description)
        
        # Save to database
        session = AnalysisSession.objects.create(
            resume_file=resume_file,
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
                resume_file=session.resume_file,
                resume_text=session.resume_text,
                job_description=session.job_description,
                match_percentage=session.match_percentage,
                matching_skills=session.matching_skills,
                matching_education=session.matching_education,
                matching_experience=session.matching_experience,
                highlighted_strengths=session.highlighted_strengths,
                identified_gaps=session.identified_gaps
            )
            logger.info(f"Qualified candidate saved: {qualified_candidate.id} with {session.match_percentage}% match")
        
        # Clean up temp file
        default_storage.delete(file_path)
        
        # Prepare response
        response_data = {
            'session_id': session.id,
            'match_percentage': session.match_percentage,
            'matching_skills': session.matching_skills,
            'matching_education': session.matching_education,
            'matching_experience': session.matching_experience,
            'highlighted_strengths': session.highlighted_strengths,
            'identified_gaps': session.identified_gaps,
            'processing_time': session.processing_time,
            'created_at': session.created_at,
            'is_qualified': is_qualified
        }
        
        response_serializer = AnalysisResponseSerializer(response_data)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return Response(
            {'error': f'Analysis failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_analysis(request, session_id):
    """
    Retrieve analysis by session ID
    
    GET /api/django/analysis/{session_id}/
    """
    try:
        session = AnalysisSession.objects.get(id=session_id)
        serializer = AnalysisSessionSerializer(session)
        return Response(serializer.data)
    except AnalysisSession.DoesNotExist:
        return Response(
            {'error': 'Analysis session not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def list_analyses(request):
    """
    List all analysis sessions
    
    GET /api/django/analyses/
    """
    sessions = AnalysisSession.objects.all()
    serializer = AnalysisSessionSerializer(sessions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def list_qualified_candidates(request):
    """
    List all qualified candidates (>80% match)
    
    GET /api/django/qualified-candidates/
    
    Query parameters:
        - status: Filter by status (NEW, REVIEWED, CONTACTED, etc.)
        - min_percentage: Minimum match percentage (default: 80)
        - highly_qualified: true/false - Filter for >90% match
    """
    queryset = QualifiedCandidate.objects.all()
    
    # Filter by status
    status_filter = request.query_params.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter.upper())
    
    # Filter by minimum percentage
    min_percentage = request.query_params.get('min_percentage', 80)
    try:
        queryset = queryset.filter(match_percentage__gte=float(min_percentage))
    except ValueError:
        pass
    
    # Filter for highly qualified (>90%)
    highly_qualified = request.query_params.get('highly_qualified')
    if highly_qualified and highly_qualified.lower() == 'true':
        queryset = queryset.filter(match_percentage__gte=90.0)
    
    serializer = QualifiedCandidateListSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_qualified_candidate(request, candidate_id):
    """
    Retrieve qualified candidate by ID
    
    GET /api/django/qualified-candidates/{candidate_id}/
    """
    try:
        candidate = QualifiedCandidate.objects.get(id=candidate_id)
        serializer = QualifiedCandidateSerializer(candidate)
        return Response(serializer.data)
    except QualifiedCandidate.DoesNotExist:
        return Response(
            {'error': 'Qualified candidate not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PATCH'])
def update_qualified_candidate(request, candidate_id):
    """
    Update qualified candidate details
    
    PATCH /api/django/qualified-candidates/{candidate_id}/
    
    Body (JSON):
        - status: string (NEW, REVIEWED, CONTACTED, INTERVIEWING, HIRED, REJECTED)
        - is_contacted: boolean
        - notes: string
    """
    try:
        candidate = QualifiedCandidate.objects.get(id=candidate_id)
        serializer = QualifiedCandidateSerializer(
            candidate, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except QualifiedCandidate.DoesNotExist:
        return Response(
            {'error': 'Qualified candidate not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def qualified_candidates_stats(request):
    """
    Get statistics about qualified candidates
    
    GET /api/django/qualified-candidates/stats/
    """
    total_qualified = QualifiedCandidate.objects.count()
    highly_qualified = QualifiedCandidate.objects.filter(match_percentage__gte=90.0).count()
    
    status_breakdown = {}
    for status_choice in QualifiedCandidate.STATUS_CHOICES:
        status_code = status_choice[0]
        count = QualifiedCandidate.objects.filter(status=status_code).count()
        status_breakdown[status_code] = count
    
    return Response({
        'total_qualified_candidates': total_qualified,
        'highly_qualified_count': highly_qualified,
        'status_breakdown': status_breakdown,
        'contacted_count': QualifiedCandidate.objects.filter(is_contacted=True).count(),
        'not_contacted_count': QualifiedCandidate.objects.filter(is_contacted=False).count()
    })


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({'status': 'healthy', 'service': 'django'})