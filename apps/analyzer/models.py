from django.db import models
from django.core.validators import FileExtensionValidator
import uuid

class AnalysisSession(models.Model):
    """Stores analysis results for resume and JD comparison"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Input files
    resume_file = models.FileField(
        upload_to='resumes/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf'])],
        help_text='PDF resume file'
    )
    job_description = models.TextField(help_text='Job description text')
    
    # Extracted text
    resume_text = models.TextField(blank=True)
    
    # Analysis results
    match_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    matching_skills = models.JSONField(default=list, blank=True)
    matching_education = models.TextField(blank=True)
    matching_experience = models.TextField(blank=True)
    highlighted_strengths = models.JSONField(default=list, blank=True)
    identified_gaps = models.JSONField(default=list, blank=True)
    
    # Full AI response
    ai_response = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processing_time = models.FloatField(null=True, blank=True, help_text='Processing time in seconds')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Analysis Session'
        verbose_name_plural = 'Analysis Sessions'
    
    def __str__(self):
        return f"Analysis {self.id} - {self.match_percentage}%"