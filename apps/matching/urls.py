"""
URL configuration for matching app
"""
from django.urls import path
from .views import (
    MatchingCandidatesView,
    MatchingJobsView,
    SkillGapAnalysisView,
    CalculateMatchScoreView,
)

app_name = 'matching'

urlpatterns = [
    path('candidates/<int:job_id>/', MatchingCandidatesView.as_view(), name='matching-candidates'),
    path('jobs/', MatchingJobsView.as_view(), name='matching-jobs'),
    path('skill-gap/<int:job_id>/', SkillGapAnalysisView.as_view(), name='skill-gap'),
    path('calculate/', CalculateMatchScoreView.as_view(), name='calculate-score'),
]
