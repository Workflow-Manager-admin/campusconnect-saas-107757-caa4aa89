import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


class UserRole(models.TextChoices):
    STUDENT = 'student', 'Student'
    COLLEGE_ADMIN = 'college_admin', 'College Admin'
    TPO = 'tpo', 'TPO'
    SUPER_ADMIN = 'super_admin', 'Super Admin'


class ApplicationStatus(models.TextChoices):
    APPLIED = 'applied', 'Applied'
    SHORTLISTED = 'shortlisted', 'Shortlisted'
    SELECTED = 'selected', 'Selected'
    REJECTED = 'rejected', 'Rejected'
    WITHDRAWN = 'withdrawn', 'Withdrawn'


class PlacementRoundType(models.TextChoices):
    WRITTEN_TEST = 'written_test', 'Written Test'
    TECHNICAL_INTERVIEW = 'technical_interview', 'Technical Interview'
    HR_INTERVIEW = 'hr_interview', 'HR Interview'
    GROUP_DISCUSSION = 'group_discussion', 'Group Discussion'
    PRESENTATION = 'presentation', 'Presentation'
    FINAL_INTERVIEW = 'final_interview', 'Final Interview'


class PlacementRoundStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class JobStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    ACTIVE = 'active', 'Active'
    CLOSED = 'closed', 'Closed'
    CANCELLED = 'cancelled', 'Cancelled'


class NotificationType(models.TextChoices):
    EMAIL = 'email', 'Email'
    SMS = 'sms', 'SMS'
    IN_APP = 'in_app', 'In App'
    PUSH = 'push', 'Push'


class NotificationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SENT = 'sent', 'Sent'
    DELIVERED = 'delivered', 'Delivered'
    FAILED = 'failed', 'Failed'


class DocumentType(models.TextChoices):
    RESUME = 'resume', 'Resume'
    COVER_LETTER = 'cover_letter', 'Cover Letter'
    TRANSCRIPT = 'transcript', 'Transcript'
    CERTIFICATE = 'certificate', 'Certificate'
    PHOTO = 'photo', 'Photo'
    ID_PROOF = 'id_proof', 'ID Proof'
    OTHER = 'other', 'Other'


class AnalyticsEventType(models.TextChoices):
    LOGIN = 'login', 'Login'
    LOGOUT = 'logout', 'Logout'
    JOB_VIEW = 'job_view', 'Job View'
    JOB_APPLY = 'job_apply', 'Job Apply'
    PROFILE_UPDATE = 'profile_update', 'Profile Update'
    DOCUMENT_UPLOAD = 'document_upload', 'Document Upload'
    PLACEMENT_ROUND_UPDATE = 'placement_round_update', 'Placement Round Update'


# PUBLIC_INTERFACE
class User(models.Model):
    """
    Base user model for all user types in the campus recruitment system.
    Extends Django's user model with additional fields for campus recruitment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    updated_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_users')

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


# PUBLIC_INTERFACE
class College(models.Model):
    """
    College/institution information and subscription details.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='India')
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    subscription_plan = models.CharField(max_length=50, default='basic')
    subscription_expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_colleges')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_colleges')

    class Meta:
        db_table = 'colleges'

    def __str__(self):
        return f"{self.name} ({self.code})"


# PUBLIC_INTERFACE
class CollegeAdmin(models.Model):
    """
    TPO and admin users linked to colleges.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    permissions = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'college_admins'
        unique_together = ['user', 'college']

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.college.name}"


# PUBLIC_INTERFACE
class StudentProfile(models.Model):
    """
    Detailed student information and academic records.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=50)
    branch = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    current_cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    total_cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    skills = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    interests = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    achievements = ArrayField(models.TextField(), blank=True, null=True)
    languages = ArrayField(models.CharField(max_length=50), blank=True, null=True)
    profile_photo_url = models.URLField(blank=True, null=True)
    resume_url = models.URLField(blank=True, null=True)
    is_placement_eligible = models.BooleanField(default=True)
    placement_status = models.CharField(max_length=50, default='available')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_profiles'
        unique_together = ['college', 'student_id']

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.student_id}"


# PUBLIC_INTERFACE
class JobPosting(models.Model):
    """
    Job opportunities posted by companies.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    job_description = models.TextField()
    job_type = models.CharField(max_length=50, default='full_time')
    location = models.CharField(max_length=255, blank=True, null=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, default='INR')
    required_skills = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    preferred_skills = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    experience_required = models.CharField(max_length=100, blank=True, null=True)
    education_requirements = models.TextField(blank=True, null=True)
    eligibility_criteria = models.TextField(blank=True, null=True)
    application_deadline = models.DateTimeField(blank=True, null=True)
    interview_process = models.TextField(blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    company_logo_url = models.URLField(blank=True, null=True)
    contact_person_name = models.CharField(max_length=100, blank=True, null=True)
    contact_person_email = models.EmailField(blank=True, null=True)
    contact_person_phone = models.CharField(max_length=20, blank=True, null=True)
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    allowed_branches = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    allowed_years = ArrayField(models.IntegerField(), blank=True, null=True)
    max_applications = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.DRAFT)
    is_featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    applications_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_jobs')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_jobs')

    class Meta:
        db_table = 'job_postings'

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"


# PUBLIC_INTERFACE
class JobApplication(models.Model):
    """
    Student applications to job postings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    cover_letter = models.TextField(blank=True, null=True)
    custom_resume_url = models.URLField(blank=True, null=True)
    application_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.APPLIED)
    applied_at = models.DateTimeField(default=timezone.now)
    status_updated_at = models.DateTimeField(default=timezone.now)
    status_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_applications'
        unique_together = ['job', 'student']

    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name} - {self.job.job_title}"


# PUBLIC_INTERFACE
class PlacementRound(models.Model):
    """
    Interview rounds and placement process stages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    round_number = models.IntegerField()
    round_name = models.CharField(max_length=100)
    round_type = models.CharField(max_length=30, choices=PlacementRoundType.choices)
    description = models.TextField(blank=True, null=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=PlacementRoundStatus.choices, default=PlacementRoundStatus.SCHEDULED)
    max_participants = models.IntegerField(blank=True, null=True)
    current_participants = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_rounds')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_rounds')

    class Meta:
        db_table = 'placement_rounds'
        unique_together = ['job', 'round_number']

    def __str__(self):
        return f"{self.job.job_title} - Round {self.round_number}: {self.round_name}"


# PUBLIC_INTERFACE
class PlacementStatusHistory(models.Model):
    """
    Audit trail of application status changes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    round = models.ForeignKey(PlacementRound, on_delete=models.SET_NULL, null=True, blank=True)
    previous_status = models.CharField(max_length=20, choices=ApplicationStatus.choices, blank=True, null=True)
    new_status = models.CharField(max_length=20, choices=ApplicationStatus.choices)
    changed_at = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'placement_status_history'

    def __str__(self):
        return f"{self.application} - {self.previous_status} → {self.new_status}"


# PUBLIC_INTERFACE
class AnalyticsLog(models.Model):
    """
    User activity and system usage tracking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=30, choices=AnalyticsEventType.choices)
    event_data = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'analytics_logs'

    def __str__(self):
        return f"{self.event_type} - {self.user} - {self.created_at}"


# PUBLIC_INTERFACE
class Notification(models.Model):
    """
    System notifications and communications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    template_id = models.CharField(max_length=100, blank=True, null=True)
    template_data = models.JSONField(default=dict)
    target_roles = ArrayField(models.CharField(max_length=20), blank=True, null=True)
    target_users = ArrayField(models.UUIDField(), blank=True, null=True)
    target_criteria = models.JSONField(default=dict)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    priority = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'notifications'

    def __str__(self):
        return f"{self.title} - {self.type}"


# PUBLIC_INTERFACE
class NotificationRecipient(models.Model):
    """
    Individual notification delivery tracking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_recipients'
        unique_together = ['notification', 'user']

    def __str__(self):
        return f"{self.notification.title} - {self.user.email}"


# PUBLIC_INTERFACE
class DocumentUpload(models.Model):
    """
    File uploads and document management.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField(blank=True, null=True)
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField(blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    file_hash = models.CharField(max_length=255, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_uploads'

    def __str__(self):
        return f"{self.file_name} - {self.document_type}"


# PUBLIC_INTERFACE
class AuditTrail(models.Model):
    """
    Complete audit trail for all system changes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField(blank=True, null=True)
    action = models.CharField(max_length=50)
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'audit_trails'

    def __str__(self):
        return f"{self.action} on {self.entity_type} - {self.user} - {self.created_at}"
