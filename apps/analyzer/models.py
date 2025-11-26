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


class QualifiedCandidate(models.Model):
    """Stores resumes with ATS match percentage > 80%"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Link to original analysis
    analysis_session = models.OneToOneField(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name='qualified_candidate',
        help_text='Reference to original analysis session'
    )
    
    # Candidate information
    resume_file = models.FileField(
        upload_to='qualified_resumes/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf'])],
        help_text='PDF resume file of qualified candidate'
    )
    resume_text = models.TextField(help_text='Extracted resume text')
    
    # Job details
    job_description = models.TextField(help_text='Job description text')
    
    # Match details
    match_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text='ATS match percentage (>80%)'
    )
    matching_skills = models.JSONField(default=list, blank=True)
    matching_education = models.TextField(blank=True)
    matching_experience = models.TextField(blank=True)
    highlighted_strengths = models.JSONField(default=list, blank=True)
    identified_gaps = models.JSONField(default=list, blank=True)
    
    # Additional metadata
    qualification_date = models.DateTimeField(auto_now_add=True)
    is_contacted = models.BooleanField(default=False, help_text='Has the candidate been contacted?')
    notes = models.TextField(blank=True, help_text='Additional notes about the candidate')
    
    # Status tracking
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('REVIEWED', 'Reviewed'),
        ('CONTACTED', 'Contacted'),
        ('INTERVIEWING', 'Interviewing'),
        ('HIRED', 'Hired'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW',
        help_text='Current status of the candidate'
    )
    
    class Meta:
        ordering = ['-match_percentage', '-qualification_date']
        verbose_name = 'Qualified Candidate'
        verbose_name_plural = 'Qualified Candidates'
        indexes = [
            models.Index(fields=['-match_percentage']),
            models.Index(fields=['status']),
            models.Index(fields=['-qualification_date']),
        ]
    
    def __str__(self):
        return f"Qualified Candidate - {self.match_percentage}% Match"
    
    @property
    def is_highly_qualified(self):
        """Check if candidate has >90% match"""
        return float(self.match_percentage) >= 90.0