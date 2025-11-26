from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
import time
import logging

from .models import AnalysisSession
from .serializers import (
    AnalysisRequestSerializer,
    AnalysisResponseSerializer,
    AnalysisSessionSerializer
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
            'created_at': session.created_at
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
def health_check(request):
    """Health check endpoint"""
    return Response({'status': 'healthy', 'service': 'django'})