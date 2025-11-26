from rest_framework import serializers
from .models import AnalysisSession


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