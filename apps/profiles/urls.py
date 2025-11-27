"""
URL configuration for profiles app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet,
    SkillViewSet,
    ProfileSkillViewSet,
    ExperienceViewSet,
    EducationViewSet,
    CertificationViewSet,
)

app_name = 'profiles'

router = DefaultRouter()
# Register specific routes BEFORE the catch-all profile route
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'profile-skills', ProfileSkillViewSet, basename='profile-skill')
router.register(r'experiences', ExperienceViewSet, basename='experience')
router.register(r'education', EducationViewSet, basename='education')
router.register(r'certifications', CertificationViewSet, basename='certification')
# Profile routes (catch-all for profile IDs) - must be LAST
router.register(r'', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
