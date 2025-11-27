"""
Serializers for jobs app
"""
from rest_framework import serializers
from .models import Job, JobSkill, Application, SavedJob
from apps.profiles.models import Skill
from apps.profiles.serializers import SkillSerializer


class JobSkillSerializer(serializers.ModelSerializer):
    """Serializer for JobSkill model"""
    
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        source='skill',
        write_only=True
    )
    
    class Meta:
        model = JobSkill
        fields = ('id', 'skill', 'skill_id', 'importance', 'is_required')


class EmployerInfoSerializer(serializers.Serializer):
    """Serializer for employer contact information"""
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    company_name = serializers.SerializerMethodField()
    
    def get_company_name(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.company_name
        return ''


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model"""
    
    employer_email = serializers.EmailField(source='employer.email', read_only=True)
    employer_name = serializers.CharField(source='employer.full_name', read_only=True)
    employer_company = serializers.SerializerMethodField()
    skills = JobSkillSerializer(source='jobskill_set', many=True, read_only=True)
    is_saved = serializers.SerializerMethodField()
    has_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = (
            'id', 'employer', 'employer_email', 'employer_name', 'employer_company',
            'title', 'description', 'requirements', 'responsibilities', 'benefits',
            'location', 'is_remote', 'employment_type', 'experience_level',
            'salary_min', 'salary_max', 'salary_currency', 'salary_period',
            'skills', 'status', 'views_count', 'applications_count',
            'created_at', 'updated_at', 'expires_at',
            'is_saved', 'has_applied'
        )
        read_only_fields = ('id', 'employer', 'views_count', 'applications_count', 'created_at', 'updated_at')
    
    def get_employer_company(self, obj):
        if hasattr(obj.employer, 'profile') and obj.employer.profile:
            return obj.employer.profile.company_name
        return ''
    
    def get_is_saved(self, obj):
        """Check if the current user has saved this job"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                # Use count() > 0 instead of exists() for djongo compatibility
                return SavedJob.objects.filter(user=request.user, job_id=obj.id).count() > 0
            except Exception:
                return False
        return False
    
    def get_has_applied(self, obj):
        """Check if the current user has applied to this job"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                # Use count() > 0 instead of exists() for djongo compatibility
                return Application.objects.filter(applicant=request.user, job_id=obj.id).count() > 0
            except Exception:
                return False
        return False


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating jobs"""
    
    skills = JobSkillSerializer(source='jobskill_set', many=True, required=False)
    
    class Meta:
        model = Job
        fields = (
            'title', 'description', 'requirements', 'responsibilities', 'benefits',
            'location', 'is_remote', 'employment_type', 'experience_level',
            'salary_min', 'salary_max', 'salary_currency', 'salary_period',
            'skills', 'status', 'expires_at'
        )
    
    def create(self, validated_data):
        """Create job with skills"""
        skills_data = validated_data.pop('jobskill_set', [])
        job = Job.objects.create(**validated_data)
        
        for skill_data in skills_data:
            JobSkill.objects.create(job=job, **skill_data)
        
        return job
    
    def update(self, instance, validated_data):
        """Update job with skills"""
        skills_data = validated_data.pop('jobskill_set', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skills_data is not None:
            # Remove old skills and add new ones
            instance.jobskill_set.all().delete()
            for skill_data in skills_data:
                JobSkill.objects.create(job=instance, **skill_data)
        
        return instance


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Application model"""
    
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.SerializerMethodField()
    job_location = serializers.CharField(source='job.location', read_only=True)
    applicant_name = serializers.SerializerMethodField()
    applicant_email = serializers.EmailField(source='applicant.email', read_only=True)
    applicant_phone = serializers.CharField(source='applicant.phone_number', read_only=True)
    employer_contact = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = (
            'id', 'job', 'job_title', 'company_name', 'job_location',
            'applicant', 'applicant_name', 'applicant_email', 'applicant_phone',
            'cover_letter', 'resume', 'status', 'match_score',
            'employer_notes', 'applied_at', 'updated_at', 'employer_contact'
        )
        read_only_fields = ('id', 'applicant', 'match_score', 'applied_at', 'updated_at')
    
    def get_company_name(self, obj):
        if hasattr(obj.job.employer, 'profile') and obj.job.employer.profile:
            return obj.job.employer.profile.company_name
        return ''
    
    def get_applicant_name(self, obj):
        if hasattr(obj.applicant, 'profile') and obj.applicant.profile:
            return obj.applicant.profile.display_name
        return obj.applicant.full_name
    
    def get_employer_contact(self, obj):
        """Only show employer contact info if application is accepted"""
        if obj.status == 'accepted':
            employer = obj.job.employer
            return {
                'email': employer.email,
                'phone': employer.phone_number,
                'name': employer.full_name,
                'company_name': employer.profile.company_name if hasattr(employer, 'profile') and employer.profile else ''
            }
        return None


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating applications"""
    
    class Meta:
        model = Application
        fields = ('job', 'cover_letter', 'resume')
    
    def validate(self, attrs):
        """Validate that user hasn't already applied"""
        job = attrs.get('job')
        user = self.context['request'].user
        
        # Use count() > 0 instead of exists() for djongo compatibility
        if Application.objects.filter(job_id=job.id, applicant=user).count() > 0:
            raise serializers.ValidationError("You have already applied to this job.")
        
        if job.status != 'active':
            raise serializers.ValidationError("This job is not accepting applications.")
        
        return attrs


class SavedJobSerializer(serializers.ModelSerializer):
    """Serializer for SavedJob model"""
    
    job = JobSerializer(read_only=True)
    
    class Meta:
        model = SavedJob
        fields = ('id', 'job', 'saved_at')
        read_only_fields = ('id', 'saved_at')
