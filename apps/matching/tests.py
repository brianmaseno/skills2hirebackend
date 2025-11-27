"""
Tests for matching algorithm
"""
import pytest
from apps.matching.services import calculate_match_score, calculate_skill_value
from apps.profiles.models import ProfileSkill


@pytest.mark.django_db
class TestMatchingAlgorithm:
    """Test skill-based matching algorithm"""
    
    def test_calculate_skill_value(self):
        """Test skill value calculation"""
        # Test beginner with no experience
        value = calculate_skill_value('beginner', 0)
        assert value == 0.6
        
        # Test advanced with 5 years
        value = calculate_skill_value('advanced', 5)
        assert value > 1.4
        
        # Test expert with 10 years
        value = calculate_skill_value('expert', 10)
        assert value > 1.8
    
    def test_perfect_match(self, job, job_seeker_user, skill):
        """Test perfect skill match"""
        profile = job_seeker_user.profile
        
        # Add matching skill to profile
        ProfileSkill.objects.create(
            profile=profile,
            skill=skill,
            level='expert',
            years_experience=10
        )
        
        score = calculate_match_score(job, profile)
        assert score > 0.8  # Should have high match score
    
    def test_no_match(self, job, job_seeker_user):
        """Test no skill match"""
        profile = job_seeker_user.profile
        
        # Profile has no skills
        score = calculate_match_score(job, profile)
        assert score == 0.0
    
    def test_partial_match(self, job, job_seeker_user, skill):
        """Test partial skill match"""
        profile = job_seeker_user.profile
        
        # Add matching skill with beginner level
        ProfileSkill.objects.create(
            profile=profile,
            skill=skill,
            level='beginner',
            years_experience=0
        )
        
        score = calculate_match_score(job, profile)
        assert 0 < score < 1.0
