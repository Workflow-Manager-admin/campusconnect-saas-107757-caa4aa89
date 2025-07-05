from django.contrib import admin
from .models import (
    User, College, CollegeAdmin, StudentProfile, JobPosting, JobApplication,
    PlacementRound, PlacementStatusHistory, AnalyticsLog, Notification,
    NotificationRecipient, DocumentUpload, AuditTrail
)


# PUBLIC_INTERFACE
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin interface for User model with comprehensive filtering and display options.
    """
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'email_verified', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


# PUBLIC_INTERFACE
@admin.register(College)
class CollegeModelAdmin(admin.ModelAdmin):
    """
    Admin interface for College model with detailed information display.
    """
    list_display = ['name', 'code', 'city', 'state', 'is_active', 'subscription_plan', 'created_at']
    list_filter = ['is_active', 'subscription_plan', 'state', 'country', 'created_at']
    search_fields = ['name', 'code', 'city', 'contact_email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


# PUBLIC_INTERFACE
@admin.register(CollegeAdmin)
class CollegeAdminModelAdmin(admin.ModelAdmin):
    """
    Admin interface for CollegeAdmin model showing admin-college relationships.
    """
    list_display = ['user', 'college', 'designation', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'designation', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'college__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


# PUBLIC_INTERFACE
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for StudentProfile model with academic information display.
    """
    list_display = ['user', 'student_id', 'college', 'branch', 'year_of_study', 'current_cgpa', 'is_placement_eligible']
    list_filter = ['college', 'branch', 'year_of_study', 'is_placement_eligible', 'placement_status', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'student_id', 'college__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


# PUBLIC_INTERFACE
@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    """
    Admin interface for JobPosting model with job details and statistics.
    """
    list_display = ['job_title', 'company_name', 'college', 'status', 'application_deadline', 'applications_count', 'created_at']
    list_filter = ['status', 'job_type', 'college', 'is_featured', 'created_at']
    search_fields = ['job_title', 'company_name', 'college__name']
    readonly_fields = ['id', 'views_count', 'applications_count', 'created_at', 'updated_at']
    ordering = ['-created_at']


# PUBLIC_INTERFACE
@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """
    Admin interface for JobApplication model showing application status and details.
    """
    list_display = ['student', 'job', 'status', 'applied_at', 'score']
    list_filter = ['status', 'applied_at', 'job__college']
    search_fields = ['student__user__email', 'student__user__first_name', 'student__user__last_name', 'job__job_title', 'job__company_name']
    readonly_fields = ['id', 'applied_at', 'created_at', 'updated_at']
    ordering = ['-applied_at']


# PUBLIC_INTERFACE
@admin.register(PlacementRound)
class PlacementRoundAdmin(admin.ModelAdmin):
    """
    Admin interface for PlacementRound model with scheduling and status information.
    """
    list_display = ['job', 'round_number', 'round_name', 'round_type', 'status', 'scheduled_at', 'current_participants']
    list_filter = ['round_type', 'status', 'scheduled_at', 'created_at']
    search_fields = ['job__job_title', 'job__company_name', 'round_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['job', 'round_number']


# PUBLIC_INTERFACE
@admin.register(PlacementStatusHistory)
class PlacementStatusHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for PlacementStatusHistory model showing status change audit trail.
    """
    list_display = ['application', 'previous_status', 'new_status', 'changed_at', 'changed_by']
    list_filter = ['previous_status', 'new_status', 'changed_at']
    search_fields = ['application__student__user__email', 'application__job__job_title']
    readonly_fields = ['id', 'changed_at']
    ordering = ['-changed_at']


# PUBLIC_INTERFACE
@admin.register(AnalyticsLog)
class AnalyticsLogAdmin(admin.ModelAdmin):
    """
    Admin interface for AnalyticsLog model for tracking user activities.
    """
    list_display = ['user', 'event_type', 'college', 'created_at']
    list_filter = ['event_type', 'created_at', 'college']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']


# PUBLIC_INTERFACE
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for Notification model with delivery status and targeting information.
    """
    list_display = ['title', 'type', 'college', 'status', 'scheduled_at', 'created_at']
    list_filter = ['type', 'status', 'college', 'priority', 'created_at']
    search_fields = ['title', 'message', 'college__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


# PUBLIC_INTERFACE
@admin.register(NotificationRecipient)
class NotificationRecipientAdmin(admin.ModelAdmin):
    """
    Admin interface for NotificationRecipient model showing individual delivery tracking.
    """
    list_display = ['notification', 'user', 'status', 'sent_at', 'delivered_at', 'read_at']
    list_filter = ['status', 'sent_at', 'delivered_at', 'read_at']
    search_fields = ['notification__title', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


# PUBLIC_INTERFACE
@admin.register(DocumentUpload)
class DocumentUploadAdmin(admin.ModelAdmin):
    """
    Admin interface for DocumentUpload model with file management and verification status.
    """
    list_display = ['file_name', 'document_type', 'user', 'college', 'is_verified', 'created_at']
    list_filter = ['document_type', 'is_verified', 'is_public', 'college', 'created_at']
    search_fields = ['file_name', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'file_size', 'file_hash', 'created_at', 'updated_at']
    ordering = ['-created_at']


# PUBLIC_INTERFACE
@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    """
    Admin interface for AuditTrail model showing complete system change history.
    """
    list_display = ['entity_type', 'action', 'user', 'college', 'created_at']
    list_filter = ['entity_type', 'action', 'college', 'created_at']
    search_fields = ['entity_type', 'action', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
