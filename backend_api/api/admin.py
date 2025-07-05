from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, College, Department, StudentProfile, Company, Job, 
    Application, PlacementRound, RoundParticipation, Placement,
    Notification, AuditLog, SystemConfiguration
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom user admin
    """
    list_display = ['username', 'email', 'user_type', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'phone', 'profile_photo')
        }),
    )


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    """
    College admin interface
    """
    list_display = ['name', 'code', 'city', 'state', 'is_active', 'created_at']
    list_filter = ['is_active', 'state', 'country', 'created_at']
    search_fields = ['name', 'code', 'city']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Department admin interface
    """
    list_display = ['name', 'code', 'college', 'is_active', 'created_at']
    list_filter = ['is_active', 'college', 'created_at']
    search_fields = ['name', 'code', 'college__name']
    readonly_fields = ['created_at']


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """
    Student profile admin interface
    """
    list_display = ['user', 'student_id', 'college', 'department', 'cgpa', 'is_placed', 'created_at']
    list_filter = ['is_placed', 'placement_ready', 'college', 'department', 'graduation_year']
    search_fields = ['user__username', 'user__email', 'student_id', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Company admin interface
    """
    list_display = ['name', 'company_type', 'industry', 'is_active', 'created_at']
    list_filter = ['company_type', 'industry', 'is_active', 'created_at']
    search_fields = ['name', 'industry']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """
    Job admin interface
    """
    list_display = ['title', 'company', 'job_type', 'status', 'application_deadline', 'created_at']
    list_filter = ['job_type', 'status', 'company', 'college', 'created_at']
    search_fields = ['title', 'company__name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['eligible_departments']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """
    Application admin interface
    """
    list_display = ['student', 'job', 'status', 'applied_at']
    list_filter = ['status', 'job__company', 'applied_at']
    search_fields = ['student__user__username', 'job__title', 'job__company__name']
    readonly_fields = ['applied_at', 'updated_at']


@admin.register(PlacementRound)
class PlacementRoundAdmin(admin.ModelAdmin):
    """
    Placement round admin interface
    """
    list_display = ['title', 'job', 'round_type', 'round_number', 'scheduled_date', 'status']
    list_filter = ['round_type', 'status', 'scheduled_date', 'job__company']
    search_fields = ['title', 'job__title', 'job__company__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RoundParticipation)
class RoundParticipationAdmin(admin.ModelAdmin):
    """
    Round participation admin interface
    """
    list_display = ['student', 'round', 'status', 'score', 'created_at']
    list_filter = ['status', 'round__round_type', 'created_at']
    search_fields = ['student__user__username', 'round__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    """
    Placement admin interface
    """
    list_display = ['student', 'job', 'salary_offered', 'status', 'joining_date', 'offered_at']
    list_filter = ['status', 'job__company', 'offered_at', 'joining_date']
    search_fields = ['student__user__username', 'job__title', 'job__company__name']
    readonly_fields = ['offered_at', 'created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Notification admin interface
    """
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_email_sent', 'is_sms_sent', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']
    readonly_fields = ['created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Audit log admin interface
    """
    list_display = ['user', 'action', 'resource_type', 'resource_id', 'created_at']
    list_filter = ['action', 'resource_type', 'created_at']
    search_fields = ['user__username', 'resource_type', 'description']
    readonly_fields = ['created_at']


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    """
    System configuration admin interface
    """
    list_display = ['key', 'value', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']
