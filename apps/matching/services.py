"""
Skill-based matching services for SkillMatchHub
"""
import math
from typing import Dict, List, Tuple
from apps.jobs.models import Job, JobSkill
from apps.profiles.models import Profile, ProfileSkill


# Skill level weights
LEVEL_WEIGHTS = {
    'beginner': 0.6,
    'intermediate': 1.0,
    'advanced': 1.4,
    'expert': 1.8,
}


def calculate_skill_value(level: str, years_experience: float) -> float:
    """
    Calculate a numerical value for a skill based on level and years of experience.
    
    Args:
        level: Skill proficiency level
        years_experience: Years of experience with the skill
    
    Returns:
        Float value representing skill competency (0-2.5 range typically)
    """
    base_weight = LEVEL_WEIGHTS.get(level, 1.0)
    experience_factor = math.log(1 + years_experience) * 0.15  # Logarithmic scaling for experience
    return base_weight + experience_factor


def calculate_match_score(job: Job, profile: Profile) -> float:
    """
    Calculate match score between a job and a candidate profile.
    
    The algorithm considers:
    - Skill overlap between job requirements and candidate skills
    - Importance weight of each required skill
    - Candidate's proficiency level in each skill
    - Years of experience with each skill
    
    Args:
        job: Job instance
        profile: Profile instance
    
    Returns:
        Float between 0 and 1 representing match percentage
    """
    try:
        # Get job required skills with importance weights
        # Note: Removed select_related due to djongo/MongoDB limitations
        job_skills = list(job.jobskill_set.all().order_by())
        
        if not job_skills:
            return 0.0
        
        # Build dictionary of job requirements: {skill_name: (importance, is_required)}
        job_requirements: Dict[str, Tuple[float, bool]] = {}
        total_importance = 0.0
        
        for js in job_skills:
            try:
                skill_name = js.skill.name.lower()
                job_requirements[skill_name] = (js.importance, js.is_required)
                total_importance += js.importance
            except Exception:
                continue
        
        if total_importance == 0:
            return 0.0
        
        # Get candidate skills
        # Note: Removed select_related due to djongo/MongoDB limitations
        candidate_skills = list(profile.profileskill_set.all().order_by())
        
        # Build dictionary of candidate skills: {skill_name: skill_value}
        candidate_skill_values: Dict[str, float] = {}
        
        for ps in candidate_skills:
            try:
                skill_name = ps.skill.name.lower()
                skill_value = calculate_skill_value(ps.level, ps.years_experience)
                candidate_skill_values[skill_name] = skill_value
            except Exception:
                continue
        
        # Calculate weighted match score
        matched_importance = 0.0
        required_skills_met = 0
        total_required_skills = sum(1 for _, (_, is_req) in job_requirements.items() if is_req)
        
        for skill_name, (importance, is_required) in job_requirements.items():
            if skill_name in candidate_skill_values:
                # Candidate has this skill
                candidate_value = candidate_skill_values[skill_name]
                
                # Normalize candidate value (assuming max realistic value is 2.5)
                normalized_value = min(candidate_value / 2.5, 1.0)
                
                # Add weighted contribution
                matched_importance += importance * normalized_value
                
                if is_required:
                    required_skills_met += 1
        
        # Calculate base match score
        base_score = matched_importance / total_importance if total_importance > 0 else 0
        
        # Apply penalty if required skills are missing
        if total_required_skills > 0:
            required_ratio = required_skills_met / total_required_skills
            
            # Strong penalty for missing required skills
            if required_ratio < 1.0:
                base_score *= (0.5 + 0.5 * required_ratio)  # Max 50% penalty
        
        return round(base_score, 3)
    except Exception:
        return 0.0


def find_matching_candidates(job: Job, limit: int = 50, min_score: float = 0.3) -> List[Tuple[Profile, float]]:
    """
    Find and rank candidates that match a job posting.
    
    Args:
        job: Job instance
        limit: Maximum number of candidates to return
        min_score: Minimum match score to include (0-1)
    
    Returns:
        List of tuples (Profile, score) sorted by score descending
    """
    try:
        # Get all job seeker profiles that are available and public
        # Note: Removed select_related and prefetch_related due to djongo/MongoDB limitations
        profiles = list(Profile.objects.filter(
            user__user_type='job_seeker',
            is_public=True,
            is_available=True
        ).order_by())
        
        # Calculate match scores
        matches = []
        for profile in profiles:
            score = calculate_match_score(job, profile)
            if score >= min_score:
                matches.append((profile, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:limit]
    except Exception:
        return []


def find_matching_jobs(profile: Profile, limit: int = 50, min_score: float = 0.3) -> List[Tuple[Job, float]]:
    """
    Find and rank jobs that match a candidate's profile.
    
    Args:
        profile: Profile instance
        limit: Maximum number of jobs to return
        min_score: Minimum match score to include (0-1)
    
    Returns:
        List of tuples (Job, score) sorted by score descending
    """
    try:
        # Get all active jobs
        # Note: Removed select_related and prefetch_related due to djongo/MongoDB limitations
        jobs = list(Job.objects.filter(
            status='active'
        ).order_by())
        
        # Calculate match scores
        matches = []
        for job in jobs:
            score = calculate_match_score(job, profile)
            if score >= min_score:
                matches.append((job, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:limit]
    except Exception:
        return []


def get_skill_gap_analysis(job: Job, profile: Profile) -> Dict:
    """
    Analyze the skill gap between a job requirement and candidate profile.
    
    Args:
        job: Job instance
        profile: Profile instance
    
    Returns:
        Dictionary with matched skills, missing skills, and recommendations
    """
    try:
        # Note: Removed select_related due to djongo/MongoDB limitations
        job_skills = list(job.jobskill_set.all().order_by())
        profile_skills = list(profile.profileskill_set.all().order_by())
        
        candidate_skills_dict = {}
        for ps in profile_skills:
            try:
                candidate_skills_dict[ps.skill.name.lower()] = ps
            except Exception:
                continue
        
        matched_skills = []
        missing_skills = []
        improvement_areas = []
        
        for js in job_skills:
            try:
                skill_name = js.skill.name.lower()
                
                if skill_name in candidate_skills_dict:
                    ps = candidate_skills_dict[skill_name]
                    matched_skills.append({
                        'skill': js.skill.name,
                        'required_importance': js.importance,
                        'is_required': js.is_required,
                        'candidate_level': ps.level,
                        'candidate_experience': ps.years_experience,
                    })
                    
                    # Suggest improvement if below advanced level for important skills
                    if js.importance >= 0.8 and ps.level in ['beginner', 'intermediate']:
                        improvement_areas.append({
                            'skill': js.skill.name,
                            'current_level': ps.level,
                            'suggested_level': 'advanced',
                        })
                else:
                    missing_skills.append({
                        'skill': js.skill.name,
                        'importance': js.importance,
                        'is_required': js.is_required,
                    })
            except Exception:
                continue
        
        return {
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'improvement_areas': improvement_areas,
            'match_score': calculate_match_score(job, profile),
        }
    except Exception:
        return {
            'matched_skills': [],
            'missing_skills': [],
            'improvement_areas': [],
            'match_score': 0.0,
        }
