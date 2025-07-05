from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser
    """
    USER_TYPES = [
        ('student', 'Student'),
        ('tpo', 'Training & Placement Officer'),
        ('admin', 'College Admin'),
        ('super_admin', 'Super Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'


class College(models.Model):
    """
    College/Institution model
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='colleges/', blank=True, null=True)
    established_year = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'colleges'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """
    Academic departments/branches
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'departments'
        unique_together = ['college', 'code']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.college.name} - {self.name}"


class StudentProfile(models.Model):
    """
    Student profile with academic and personal details
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='students')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    student_id = models.CharField(max_length=50)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Personal Details
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    # Academic Details
    admission_year = models.IntegerField()
    graduation_year = models.IntegerField()
    current_semester = models.IntegerField(blank=True, null=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # 10th Grade
    tenth_board = models.CharField(max_length=100, blank=True, null=True)
    tenth_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    tenth_year = models.IntegerField(blank=True, null=True)
    
    # 12th Grade
    twelfth_board = models.CharField(max_length=100, blank=True, null=True)
    twelfth_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    twelfth_year = models.IntegerField(blank=True, null=True)
    
    # Documents
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    tenth_certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    twelfth_certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    
    # Placement Status
    is_placed = models.BooleanField(default=False)
    placement_ready = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_profiles'
        unique_together = ['college', 'student_id']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"


class Company(models.Model):
    """
    Company/Organization model
    """
    COMPANY_TYPES = [
        ('mnc', 'Multinational Corporation'),
        ('startup', 'Startup'),
        ('psu', 'Public Sector Undertaking'),
        ('government', 'Government'),
        ('consulting', 'Consulting'),
        ('product', 'Product Company'),
        ('service', 'Service Company'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='companies/', blank=True, null=True)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    headquarters = models.CharField(max_length=200, blank=True, null=True)
    employee_count = models.IntegerField(blank=True, null=True)
    founded_year = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'companies'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Job(models.Model):
    """
    Job posting model
    """
    JOB_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='jobs')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    location = models.CharField(max_length=200)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, default='INR')
    
    # Eligibility Criteria
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    eligible_departments = models.ManyToManyField(Department, blank=True)
    eligible_batches = models.CharField(max_length=100, blank=True, null=True)  # e.g., "2024,2025"
    
    # Requirements
    required_skills = models.TextField(blank=True, null=True)
    experience_required = models.TextField(blank=True, null=True)
    
    # Dates
    application_deadline = models.DateTimeField()
    interview_date = models.DateField(blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    max_applications = models.IntegerField(blank=True, null=True)
    
    # Metadata
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.company.name}"


class Application(models.Model):
    """
    Student job application model
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('screening', 'Under Screening'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('selected', 'Selected'),
        ('offered', 'Offered'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    cover_letter = models.TextField(blank=True, null=True)
    additional_documents = models.FileField(upload_to='applications/', blank=True, null=True)
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'applications'
        unique_together = ['job', 'student']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.job.title}"


class PlacementRound(models.Model):
    """
    Placement round/process model
    """
    ROUND_TYPES = [
        ('aptitude', 'Aptitude Test'),
        ('technical', 'Technical Round'),
        ('hr', 'HR Round'),
        ('group_discussion', 'Group Discussion'),
        ('presentation', 'Presentation'),
        ('case_study', 'Case Study'),
        ('final', 'Final Round'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='placement_rounds')
    round_type = models.CharField(max_length=20, choices=ROUND_TYPES)
    round_number = models.IntegerField()
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    venue = models.CharField(max_length=200, blank=True, null=True)
    
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Participants
    participants = models.ManyToManyField(StudentProfile, through='RoundParticipation', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'placement_rounds'
        unique_together = ['job', 'round_number']
        ordering = ['job', 'round_number']
    
    def __str__(self):
        return f"{self.job.title} - Round {self.round_number}"


class RoundParticipation(models.Model):
    """
    Student participation in placement rounds
    """
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('attended', 'Attended'),
        ('absent', 'Absent'),
        ('qualified', 'Qualified'),
        ('disqualified', 'Disqualified'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    round = models.ForeignKey(PlacementRound, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')
    score = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'round_participations'
        unique_together = ['round', 'student']


class Placement(models.Model):
    """
    Final placement/offer model
    """
    STATUS_CHOICES = [
        ('offered', 'Offered'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('joined', 'Joined'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='placements')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='placements')
    
    offer_letter = models.FileField(upload_to='offers/', blank=True, null=True)
    salary_offered = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    joining_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offered')
    
    offered_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    joined_at = models.DateTimeField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'placements'
        ordering = ['-offered_at']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.job.company.name}"


class Notification(models.Model):
    """
    Notification model for system notifications
    """
    NOTIFICATION_TYPES = [
        ('job_posted', 'Job Posted'),
        ('application_status', 'Application Status Update'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('placement_offer', 'Placement Offer'),
        ('system', 'System Notification'),
        ('announcement', 'Announcement'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', blank=True, null=True)
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    is_sms_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"


class AuditLog(models.Model):
    """
    Audit log for tracking user actions
    """
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'View'),
        ('download', 'Download'),
        ('upload', 'Upload'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=50)  # Model name
    resource_id = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.resource_type}"


class SystemConfiguration(models.Model):
    """
    System configuration settings
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_configurations'
        ordering = ['key']
    
    def __str__(self):
        return self.key
