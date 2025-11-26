from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('analyze/', views.analyze_resume, name='analyze-resume'),
    path('analysis/<uuid:session_id>/', views.get_analysis, name='get-analysis'),
    path('analyses/', views.list_analyses, name='list-analyses'),
]