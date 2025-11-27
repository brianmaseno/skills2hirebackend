"""
Views for profiles app
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Profile, Skill, ProfileSkill, Experience, Education, Certification
from .serializers import (
    ProfileSerializer,
    ProfileCreateUpdateSerializer,
    SkillSerializer,
    ProfileSkillSerializer,
    ExperienceSerializer,
    EducationSerializer,
    CertificationSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for Profile model"""
    
    # Note: Removed select_related and prefetch_related due to djongo/MongoDB limitations
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['location', 'is_available']
    search_fields = ['display_name', 'bio', 'headline', 'company_name']
    # Note: Removed OrderingFilter due to djongo/MongoDB limitations
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            return ProfileCreateUpdateSerializer
        return ProfileSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        if self.action == 'list':
            # Only show public profiles or user's own profile
            return self.queryset.filter(is_public=True)
        return self.queryset
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update the current user's profile"""
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.method == 'GET':
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = ProfileCreateUpdateSerializer(profile, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(ProfileSerializer(profile).data)


class SkillViewSet(viewsets.ModelViewSet):
    """ViewSet for Skill model"""
    
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    # Note: Removed OrderingFilter due to djongo/MongoDB limitations


class ProfileSkillViewSet(viewsets.ModelViewSet):
    """ViewSet for ProfileSkill model"""
    
    serializer_class = ProfileSkillSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return profile skills for the current user's profile"""
        # Note: Removed select_related due to djongo/MongoDB limitations
        return ProfileSkill.objects.filter(profile__user=self.request.user)
    
    def perform_create(self, serializer):
        """Create a profile skill for the current user's profile"""
        serializer.save(profile=self.request.user.profile)


class ExperienceViewSet(viewsets.ModelViewSet):
    """ViewSet for Experience model"""
    
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return experiences for the current user's profile"""
        return Experience.objects.filter(profile__user=self.request.user)
    
    def perform_create(self, serializer):
        """Create an experience for the current user's profile"""
        serializer.save(profile=self.request.user.profile)


class EducationViewSet(viewsets.ModelViewSet):
    """ViewSet for Education model"""
    
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return education for the current user's profile"""
        return Education.objects.filter(profile__user=self.request.user)
    
    def perform_create(self, serializer):
        """Create an education entry for the current user's profile"""
        serializer.save(profile=self.request.user.profile)


class CertificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Certification model"""
    
    serializer_class = CertificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return certifications for the current user's profile"""
        return Certification.objects.filter(profile__user=self.request.user)
    
    def perform_create(self, serializer):
        """Create a certification for the current user's profile"""
        serializer.save(profile=self.request.user.profile)
