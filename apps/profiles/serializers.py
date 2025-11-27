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
    
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        source='skill',
        write_only=True
    )
    
    class Meta:
        model = ProfileSkill
        fields = ('id', 'skill', 'skill_id', 'level', 'years_experience', 'is_verified')


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
    skills = ProfileSkillSerializer(source='profileskill_set', many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    
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
