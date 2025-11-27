"""
URL configuration for jobs app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewSet, ApplicationViewSet, SavedJobViewSet

app_name = 'jobs'

router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'saved', SavedJobViewSet, basename='saved-job')

urlpatterns = [
    path('', include(router.urls)),
]
