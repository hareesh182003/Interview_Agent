from django.contrib import admin
from .models import AnalysisSession, QualifiedCandidate
from rangefilter.filters import NumericRangeFilter

@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'match_percentage', 'created_at', 'processing_time']
    list_filter = ['created_at']
    search_fields = ['id', 'job_description', 'resume_text']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Session Info', {
            'fields': ('id', 'created_at', 'updated_at', 'processing_time')
        }),
        ('Input', {
            'fields': ('resume_file', 'job_description', 'resume_text')
        }),
        ('Analysis Results', {
            'fields': (
                'match_percentage',
                'matching_skills',
                'matching_education',
                'matching_experience',
                'highlighted_strengths',
                'identified_gaps',
                'ai_response'
            )
        }),
    )


@admin.register(QualifiedCandidate)
class QualifiedCandidateAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'match_percentage',
        'status',
        'is_contacted',
        'qualification_date',
        'is_highly_qualified'
    ]
    list_filter = [
        'status',
        'is_contacted',
        'qualification_date',
        ('match_percentage', NumericRangeFilter)
    ]
    search_fields = ['id', 'job_description', 'resume_text', 'notes']
    readonly_fields = ['id', 'analysis_session', 'qualification_date', 'is_highly_qualified']
    
    fieldsets = (
        ('Candidate Info', {
            'fields': (
                'id',
                'analysis_session',
                'qualification_date',
                'is_highly_qualified'
            )
        }),
        ('Match Details', {
            'fields': (
                'match_percentage',
                'matching_skills',
                'matching_education',
                'matching_experience',
                'highlighted_strengths',
                'identified_gaps'
            )
        }),
        ('Tracking', {
            'fields': (
                'status',
                'is_contacted',
                'notes'
            )
        }),
        ('Documents', {
            'fields': (
                'resume_file',
                'job_description',
                'resume_text'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_contacted', 'mark_as_reviewed', 'mark_as_interviewing']
    
    def mark_as_contacted(self, request, queryset):
        queryset.update(is_contacted=True, status='CONTACTED')
        self.message_user(request, f'{queryset.count()} candidates marked as contacted.')
    mark_as_contacted.short_description = 'Mark selected as contacted'
    
    def mark_as_reviewed(self, request, queryset):
        queryset.update(status='REVIEWED')
        self.message_user(request, f'{queryset.count()} candidates marked as reviewed.')
    mark_as_reviewed.short_description = 'Mark selected as reviewed'
    
    def mark_as_interviewing(self, request, queryset):
        queryset.update(status='INTERVIEWING')
        self.message_user(request, f'{queryset.count()} candidates marked as interviewing.')
    mark_as_interviewing.short_description = 'Mark selected as interviewing'