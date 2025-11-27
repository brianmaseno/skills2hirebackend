"""
Views for matching app
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.jobs.models import Job
from apps.jobs.serializers import JobSerializer
from apps.profiles.models import Profile
from apps.profiles.serializers import ProfileSerializer
from .services import (
    find_matching_candidates,
    find_matching_jobs,
    get_skill_gap_analysis,
    calculate_match_score,
)


class MatchingCandidatesView(APIView):
    """
    API view to find matching candidates for a job.
    Only accessible by employers for their own jobs.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, job_id):
        """Get matching candidates for a specific job"""
        
        # Verify user is employer
        if not request.user.is_employer:
            return Response(
                {'error': 'Only employers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get job and verify ownership
        try:
            job = Job.objects.get(id=job_id, employer=request.user)
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found or you do not have permission to access it.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get parameters
        limit = int(request.query_params.get('limit', 50))
        min_score = float(request.query_params.get('min_score', 0.3))
        
        # Find matching candidates
        matches = find_matching_candidates(job, limit=limit, min_score=min_score)
        
        # Format response
        results = []
        for profile, score in matches:
            profile_data = ProfileSerializer(profile).data
            profile_data['match_score'] = score
            results.append(profile_data)
        
        return Response({
            'job_id': job_id,
            'job_title': job.title,
            'total_matches': len(results),
            'candidates': results
        })


class MatchingJobsView(APIView):
    """
    API view to find matching jobs for the current user's profile.
    Only accessible by job seekers.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get matching jobs for the current user's profile"""
        
        # Verify user is job seeker
        if not request.user.is_job_seeker:
            return Response(
                {'error': 'Only job seekers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get user's profile
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found. Please complete your profile.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get parameters
        limit = int(request.query_params.get('limit', 50))
        min_score = float(request.query_params.get('min_score', 0.3))
        
        # Find matching jobs
        matches = find_matching_jobs(profile, limit=limit, min_score=min_score)
        
        # Format response
        results = []
        for job, score in matches:
            job_data = JobSerializer(job, context={'request': request}).data
            job_data['match_score'] = score
            results.append(job_data)
        
        return Response({
            'profile_id': profile.id,
            'total_matches': len(results),
            'jobs': results
        })


class SkillGapAnalysisView(APIView):
    """
    API view to get skill gap analysis between a job and candidate.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, job_id):
        """Get skill gap analysis for a specific job"""
        
        # Verify user is job seeker
        if not request.user.is_job_seeker:
            return Response(
                {'error': 'Only job seekers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get job
        try:
            job = Job.objects.get(id=job_id, status='active')
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found or not active.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get user's profile
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found. Please complete your profile.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get skill gap analysis
        analysis = get_skill_gap_analysis(job, profile)
        
        return Response({
            'job_id': job_id,
            'job_title': job.title,
            'analysis': analysis
        })


class CalculateMatchScoreView(APIView):
    """
    API view to calculate match score between a job and candidate.
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Calculate match score"""
        
        job_id = request.data.get('job_id')
        profile_id = request.data.get('profile_id')
        
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get job
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get profile (use current user's profile if not specified)
        if profile_id:
            # Employers can check any profile against their jobs
            if not request.user.is_employer or job.employer != request.user:
                return Response(
                    {'error': 'You do not have permission to check this profile.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            try:
                profile = Profile.objects.get(id=profile_id)
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'Profile not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Use current user's profile
            try:
                profile = request.user.profile
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'Profile not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Calculate match score
        score = calculate_match_score(job, profile)
        
        return Response({
            'job_id': job_id,
            'profile_id': profile.id,
            'match_score': score
        })
