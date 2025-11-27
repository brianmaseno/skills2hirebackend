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
    
    # Note: Removed select_related and prefetch_related due to djongo/MongoDB limitations
    # djongo doesn't handle JOINs with ORDER BY properly
    queryset = Job.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['employment_type', 'experience_level', 'is_remote', 'status']
    search_fields = ['title', 'description', 'location']
    pagination_class = None  # Disable pagination for djongo compatibility
    # Note: Removed OrderingFilter due to djongo limitations with ORDER BY + JOINs
    
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
        # Simple query for djongo compatibility - just return active jobs
        # The my_jobs action handles employer's own jobs separately
        queryset = Job.objects.filter(status='active')
        
        # Filter by location (simple filter, no Q objects with OR)
        location = self.request.query_params.get('location')
        if location:
            # Just filter by location, skip OR with is_remote for djongo compatibility
            queryset = queryset.filter(location__icontains=location)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list to handle djongo compatibility"""
        try:
            queryset = self.get_queryset()
            jobs = list(queryset)
            serializer = self.get_serializer(jobs, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response([], status=status.HTTP_200_OK)
    
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
        
        # Use simple filter without JOINs for djongo compatibility
        jobs = list(Job.objects.filter(employer_id=request.user.id))
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Application model"""
    
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'job']
    pagination_class = None  # Disable pagination for djongo compatibility
    # Note: Removed OrderingFilter due to djongo/MongoDB limitations
    
    def get_queryset(self):
        """Return applications based on user type"""
        user = self.request.user
        
        if user.is_employer:
            # Employers see applications to their jobs
            # Avoid JOIN by first getting job IDs, then filtering applications
            try:
                job_ids = list(Job.objects.filter(employer_id=user.id).values_list('id', flat=True))
                if job_ids:
                    return Application.objects.filter(job_id__in=job_ids)
                return Application.objects.none()
            except Exception:
                return Application.objects.none()
        else:
            # Job seekers see their own applications
            return Application.objects.filter(applicant_id=user.id)
    
    def list(self, request, *args, **kwargs):
        """Override list to handle djongo compatibility"""
        try:
            queryset = self.get_queryset()
            applications = list(queryset)
            serializer = self.get_serializer(applications, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response([], status=status.HTTP_200_OK)
    
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
    pagination_class = None  # Disable pagination for djongo compatibility
    
    def get_queryset(self):
        """Return saved jobs for current user"""
        # Note: Removed select_related due to djongo/MongoDB JOIN limitations
        return SavedJob.objects.filter(user=self.request.user)
    
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
