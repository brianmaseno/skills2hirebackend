"""
Test configuration and fixtures
"""
import pytest
from django.contrib.auth import get_user_model
from apps.profiles.models import Profile, Skill
from apps.jobs.models import Job

User = get_user_model()


@pytest.fixture
def job_seeker_user(db):
    """Create a job seeker user"""
    user = User.objects.create_user(
        email='jobseeker@example.com',
        password='testpass123',
        user_type='job_seeker'
    )
    return user


@pytest.fixture
def employer_user(db):
    """Create an employer user"""
    user = User.objects.create_user(
        email='employer@example.com',
        password='testpass123',
        user_type='employer'
    )
    return user


@pytest.fixture
def skill(db):
    """Create a test skill"""
    skill = Skill.objects.create(
        name='Python',
        description='Python programming language'
    )
    return skill


@pytest.fixture
def job(db, employer_user, skill):
    """Create a test job"""
    job = Job.objects.create(
        employer=employer_user,
        title='Python Developer',
        description='We are looking for a Python developer',
        employment_type='full_time',
        experience_level='mid',
        status='active'
    )
    job.skills_required.add(skill)
    return job
