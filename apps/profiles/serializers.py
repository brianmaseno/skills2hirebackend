"""
Serializers for profiles app
"""
from rest_framework import serializers
from .models import Profile, Skill, ProfileSkill, Experience, Education, Certification


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model"""
    
    class Meta:
        model = Skill
        fields = ('id', 'name', 'slug', 'description', 'category')
        read_only_fields = ('slug',)


class ProfileSkillSerializer(serializers.ModelSerializer):
    """Serializer for ProfileSkill model"""
    
    skill = serializers.SerializerMethodField()
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        source='skill',
        write_only=True
    )
    
    class Meta:
        model = ProfileSkill
        fields = ('id', 'skill', 'skill_id', 'level', 'years_experience', 'is_verified')
    
    def get_skill(self, obj):
        """Get skill data with djongo-compatible query"""
        try:
            if obj.skill_id:
                skill = Skill.objects.get(id=obj.skill_id)
                return SkillSerializer(skill).data
            return None
        except Exception:
            return None


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for Experience model"""
    
    class Meta:
        model = Experience
        fields = (
            'id', 'company_name', 'job_title', 'employment_type',
            'location', 'start_date', 'end_date', 'is_current', 'description'
        )


class EducationSerializer(serializers.ModelSerializer):
    """Serializer for Education model"""
    
    class Meta:
        model = Education
        fields = (
            'id', 'institution', 'degree', 'field_of_study',
            'start_date', 'end_date', 'is_current', 'grade', 'description'
        )


class CertificationSerializer(serializers.ModelSerializer):
    """Serializer for Certification model"""
    
    class Meta:
        model = Certification
        fields = (
            'id', 'name', 'issuing_organization', 'issue_date',
            'expiry_date', 'credential_id', 'credential_url', 'is_verified'
        )


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model"""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)
    skills = serializers.SerializerMethodField()
    experiences = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = (
            'id', 'user_email', 'user_type', 'display_name', 'bio', 'headline',
            'location', 'phone', 'website', 'linkedin_url', 'github_url',
            'avatar', 'resume', 'company_name', 'company_size', 'company_website',
            'company_logo', 'skills', 'experiences', 'education', 'certifications',
            'is_public', 'is_available', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_skills(self, obj):
        """Get skills with djongo-compatible query"""
        try:
            profile_skills = list(ProfileSkill.objects.filter(profile_id=obj.id))
            return ProfileSkillSerializer(profile_skills, many=True).data
        except Exception:
            return []
    
    def get_experiences(self, obj):
        """Get experiences with djongo-compatible query"""
        try:
            experiences = list(Experience.objects.filter(profile_id=obj.id))
            return ExperienceSerializer(experiences, many=True).data
        except Exception:
            return []
    
    def get_education(self, obj):
        """Get education with djongo-compatible query"""
        try:
            education = list(Education.objects.filter(profile_id=obj.id))
            return EducationSerializer(education, many=True).data
        except Exception:
            return []
    
    def get_certifications(self, obj):
        """Get certifications with djongo-compatible query"""
        try:
            certifications = list(Certification.objects.filter(profile_id=obj.id))
            return CertificationSerializer(certifications, many=True).data
        except Exception:
            return []


class ProfileCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating profile (without nested objects)"""
    
    class Meta:
        model = Profile
        fields = (
            'display_name', 'bio', 'headline', 'location', 'phone', 'website',
            'linkedin_url', 'github_url', 'avatar', 'resume', 'company_name',
            'company_size', 'company_website', 'company_logo',
            'is_public', 'is_available'
        )
