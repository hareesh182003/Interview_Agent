from rest_framework import serializers
from .models import AnalysisSession, QualifiedCandidate


class AnalysisSessionSerializer(serializers.ModelSerializer):
    """Serializer for analysis session model"""
    
    class Meta:
        model = AnalysisSession
        fields = [
            'id',
            'resume_file',
            'job_description',
            'resume_text',
            'match_percentage',
            'matching_skills',
            'matching_education',
            'matching_experience',
            'highlighted_strengths',
            'identified_gaps',
            'ai_response',
            'created_at',
            'processing_time'
        ]
        read_only_fields = [
            'id',
            'resume_text',
            'match_percentage',
            'matching_skills',
            'matching_education',
            'matching_experience',
            'highlighted_strengths',
            'identified_gaps',
            'ai_response',
            'created_at',
            'processing_time'
        ]


class AnalysisRequestSerializer(serializers.Serializer):
    """Serializer for analysis request"""
    
    resume_file = serializers.FileField(
        help_text="PDF file of the resume",
        required=True
    )
    job_description = serializers.CharField(
        help_text="Job description text",
        required=True,
        style={'base_template': 'textarea.html'}
    )
    
    def validate_resume_file(self, value):
        """Validate resume file"""
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed")
        
        if value.size > 5 * 1024 * 1024:  # 5MB
            raise serializers.ValidationError("File size must be under 5MB")
        
        return value


class AnalysisResponseSerializer(serializers.Serializer):
    """Serializer for analysis response"""
    
    session_id = serializers.UUIDField()
    match_percentage = serializers.FloatField()
    matching_skills = serializers.ListField(child=serializers.CharField())
    matching_education = serializers.CharField()
    matching_experience = serializers.CharField()
    highlighted_strengths = serializers.ListField(child=serializers.CharField())
    identified_gaps = serializers.ListField(child=serializers.CharField())
    processing_time = serializers.FloatField()
    created_at = serializers.DateTimeField()
    is_qualified = serializers.BooleanField(default=False)


class QualifiedCandidateSerializer(serializers.ModelSerializer):
    """Serializer for qualified candidate model"""
    
    analysis_session_id = serializers.UUIDField(source='analysis_session.id', read_only=True)
    is_highly_qualified = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = QualifiedCandidate
        fields = [
            'id',
            'analysis_session_id',
            'resume_file',
            'resume_text',
            'job_description',
            'match_percentage',
            'matching_skills',
            'matching_education',
            'matching_experience',
            'highlighted_strengths',
            'identified_gaps',
            'qualification_date',
            'is_contacted',
            'notes',
            'status',
            'is_highly_qualified'
        ]
        read_only_fields = [
            'id',
            'analysis_session_id',
            'qualification_date',
            'is_highly_qualified'
        ]


class QualifiedCandidateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing qualified candidates"""
    
    is_highly_qualified = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = QualifiedCandidate
        fields = [
            'id',
            'match_percentage',
            'qualification_date',
            'status',
            'is_contacted',
            'is_highly_qualified'
        ]