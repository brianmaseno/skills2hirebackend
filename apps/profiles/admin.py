"""
Admin configuration for profiles app
"""
from django.contrib import admin
from .models import Profile, Skill, ProfileSkill, Experience, Education, Certification


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Admin configuration for Skill model"""
    
    list_display = ('name', 'slug', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class ProfileSkillInline(admin.TabularInline):
    """Inline admin for ProfileSkill"""
    model = ProfileSkill
    extra = 1


class ExperienceInline(admin.StackedInline):
    """Inline admin for Experience"""
    model = Experience
    extra = 0


class EducationInline(admin.StackedInline):
    """Inline admin for Education"""
    model = Education
    extra = 0


class CertificationInline(admin.TabularInline):
    """Inline admin for Certification"""
    model = Certification
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin configuration for Profile model"""
    
    list_display = ('display_name', 'user', 'location', 'is_public', 'is_available', 'created_at')
    list_filter = ('is_public', 'is_available', 'created_at', 'user__user_type')
    search_fields = ('display_name', 'user__email', 'company_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProfileSkillInline, ExperienceInline, EducationInline, CertificationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'display_name', 'bio', 'headline', 'location', 'phone')
        }),
        ('Online Presence', {
            'fields': ('website', 'linkedin_url', 'github_url')
        }),
        ('Files', {
            'fields': ('avatar', 'resume')
        }),
        ('Company Information (Employers)', {
            'fields': ('company_name', 'company_size', 'company_website', 'company_logo'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_public', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    """Admin configuration for Experience model"""
    
    list_display = ('profile', 'job_title', 'company_name', 'employment_type', 'start_date', 'is_current')
    list_filter = ('employment_type', 'is_current', 'start_date')
    search_fields = ('profile__display_name', 'job_title', 'company_name')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """Admin configuration for Education model"""
    
    list_display = ('profile', 'degree', 'field_of_study', 'institution', 'start_date', 'is_current')
    list_filter = ('degree', 'is_current', 'start_date')
    search_fields = ('profile__display_name', 'institution', 'field_of_study')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    """Admin configuration for Certification model"""
    
    list_display = ('profile', 'name', 'issuing_organization', 'issue_date', 'is_verified')
    list_filter = ('is_verified', 'issue_date')
    search_fields = ('profile__display_name', 'name', 'issuing_organization')
