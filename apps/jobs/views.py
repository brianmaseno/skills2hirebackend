"""
Views for jobs app
"""
from rest_framework import viewsets, status, filters, serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Job, Application, SavedJob
from .serializers import (
    JobSerializer,
    JobCreateUpdateSerializer,
    ApplicationSerializer,
    ApplicationCreateSerializer,
    SavedJobSerializer,
)


class JobViewSet(viewsets.ModelViewSet):
    """ViewSet for Job model"""
    
    queryset = Job.objects.select_related('employer__profile').prefetch_related('jobskill_set__skill')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employment_type', 'experience_level', 'is_remote', 'status']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'salary_min', 'applications_count', 'views_count']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            return JobCreateUpdateSerializer
        return JobSerializer
    
    def get_permissions(self):
        """Allow anyone to view jobs, but only authenticated employers to create/edit"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset based on user and status"""
        queryset = self.queryset
        
        if self.action == 'list':
            # For any user (authenticated or not), show active jobs
            # Employers additionally see their own jobs in all statuses
            if self.request.user.is_authenticated and hasattr(self.request.user, 'is_employer') and self.request.user.is_employer:
                # Employers see their own jobs (any status) + all active jobs
                queryset = queryset.filter(Q(employer=self.request.user) | Q(status='active'))
            else:
                # Everyone else sees only active jobs
                queryset = queryset.filter(status='active')
        
        # Filter by skills if provided
        skills = self.request.query_params.getlist('skills')
        if skills:
            queryset = queryset.filter(skills_required__id__in=skills).distinct()
        
        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(
                Q(location__icontains=location) | Q(is_remote=True)
            )
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count on retrieve"""
        instance = self.get_object()
        # Use direct increment instead of F() expression (djongo/MongoDB doesn't support F() in updates)
        instance.views_count = (instance.views_count or 0) + 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Set employer to current user"""
        if not self.request.user.is_employer:
            raise drf_serializers.ValidationError("Only employers can create jobs.")
        serializer.save(employer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_jobs(self, request):
        """Get jobs posted by the current employer"""
        if not request.user.is_employer:
            return Response(
                {'error': 'Only employers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        jobs = self.get_queryset().filter(employer=request.user)
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Application model"""
    
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'job']
    ordering_fields = ['applied_at', 'match_score']
    
    def get_queryset(self):
        """Return applications based on user type"""
        user = self.request.user
        
        if user.is_employer:
            # Employers see applications to their jobs
            return Application.objects.filter(
                job__employer=user
            ).select_related('job', 'applicant__profile')
        else:
            # Job seekers see their own applications
            return Application.objects.filter(
                applicant=user
            ).select_related('job__employer__profile')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return ApplicationCreateSerializer
        return ApplicationSerializer
    
    def perform_create(self, serializer):
        """Create application and update job applications count"""
        application = serializer.save(applicant=self.request.user)
        
        # Update applications count (use direct increment for djongo/MongoDB compatibility)
        job = application.job
        job.applications_count = (job.applications_count or 0) + 1
        job.save(update_fields=['applications_count'])
        
        # Calculate match score using matching algorithm
        from apps.matching.services import calculate_match_score
        match_score = calculate_match_score(job, self.request.user.profile)
        application.match_score = match_score
        application.save(update_fields=['match_score'])
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update application status (employers only)"""
        application = self.get_object()
        
        if not request.user.is_employer or application.job.employer != request.user:
            return Response(
                {'error': 'You do not have permission to update this application.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in dict(Application.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.status = new_status
        application.employer_notes = request.data.get('employer_notes', application.employer_notes)
        application.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)


class SavedJobViewSet(viewsets.ModelViewSet):
    """ViewSet for SavedJob model"""
    
    serializer_class = SavedJobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return saved jobs for current user"""
        return SavedJob.objects.filter(
            user=self.request.user
        ).select_related('job__employer__profile')
    
    def create(self, request, *args, **kwargs):
        """Save a job"""
        job_id = request.data.get('job_id')
        
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        saved_job, created = SavedJob.objects.get_or_create(
            user=request.user,
            job=job
        )
        
        if not created:
            return Response(
                {'message': 'Job already saved'},
                status=status.HTTP_200_OK
            )
        
        serializer = self.get_serializer(saved_job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['delete'])
    def unsave(self, request):
        """Unsave a job"""
        job_id = request.data.get('job_id')
        
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = SavedJob.objects.filter(
            user=request.user,
            job_id=job_id
        ).delete()
        
        if deleted_count == 0:
            return Response(
                {'error': 'Saved job not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {'message': 'Job unsaved successfully'},
            status=status.HTTP_200_OK
        )
