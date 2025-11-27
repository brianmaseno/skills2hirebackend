"""
Admin configuration for jobs app
"""
from django.contrib import admin
from .models import Job, JobSkill, Application, SavedJob


class JobSkillInline(admin.TabularInline):
    """Inline admin for JobSkill"""
    model = JobSkill
    extra = 1


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin configuration for Job model"""
    
    list_display = ('title', 'employer', 'employment_type', 'status', 'applications_count', 'created_at')
    list_filter = ('status', 'employment_type', 'experience_level', 'is_remote', 'created_at')
    search_fields = ('title', 'description', 'employer__email')
    readonly_fields = ('views_count', 'applications_count', 'created_at', 'updated_at')
    inlines = [JobSkillInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employer', 'title', 'description', 'requirements', 'responsibilities', 'benefits')
        }),
        ('Job Details', {
            'fields': ('employment_type', 'experience_level', 'location', 'is_remote')
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max', 'salary_currency', 'salary_period')
        }),
        ('Status & Metrics', {
            'fields': ('status', 'views_count', 'applications_count', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin configuration for Application model"""
    
    list_display = ('applicant', 'job', 'status', 'match_score', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('applicant__email', 'job__title')
    readonly_fields = ('match_score', 'applied_at', 'updated_at')
    
    fieldsets = (
        ('Application Details', {
            'fields': ('job', 'applicant', 'cover_letter', 'resume', 'status', 'match_score')
        }),
        ('Employer Section', {
            'fields': ('employer_notes',)
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    """Admin configuration for SavedJob model"""
    
    list_display = ('user', 'job', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__email', 'job__title')
    readonly_fields = ('saved_at',)
