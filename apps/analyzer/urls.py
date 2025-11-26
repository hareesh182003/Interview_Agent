from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('analyze/', views.analyze_resume, name='analyze-resume'),
    path('analysis/<uuid:session_id>/', views.get_analysis, name='get-analysis'),
    path('analyses/', views.list_analyses, name='list-analyses'),

    # Qualified candidates endpoints
    path('qualified-candidates/', views.list_qualified_candidates, name='list-qualified-candidates'),
    path('qualified-candidates/stats/', views.qualified_candidates_stats, name='qualified-candidates-stats'),
    path('qualified-candidates/<uuid:candidate_id>/', views.get_qualified_candidate, name='get-qualified-candidate'),
    path('qualified-candidates/<uuid:candidate_id>/update/', views.update_qualified_candidate, name='update-qualified-candidate'),

]