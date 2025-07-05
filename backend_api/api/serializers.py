from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import (
    User, College, CollegeAdmin, StudentProfile, JobPosting, JobApplication,
    PlacementRound, PlacementStatusHistory, AnalyticsLog, Notification,
    NotificationRecipient, DocumentUpload, AuditTrail
)


# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with password hashing and role validation.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'confirm_password', 'first_name', 'last_name',
            'phone', 'role', 'is_active', 'email_verified', 'last_login',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'last_login': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
    
    def validate(self, attrs):
        """Validate password confirmation and email uniqueness."""
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('confirm_password')
        validated_data['password_hash'] = make_password(validated_data.pop('password'))
        return super().create(validated_data)


# PUBLIC_INTERFACE
class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login with email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    if not user.is_active:
                        raise serializers.ValidationError('User account is disabled.')
                    attrs['user'] = user
                else:
                    raise serializers.ValidationError('Invalid credentials.')
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid credentials.')
        else:
            raise serializers.ValidationError('Must include email and password.')
        
        return attrs


# PUBLIC_INTERFACE
class CollegeSerializer(serializers.ModelSerializer):
    """
    Serializer for College model with comprehensive validation.
    """
    class Meta:
        model = College
        fields = [
            'id', 'name', 'code', 'address', 'city', 'state', 'country',
            'postal_code', 'website', 'contact_email', 'contact_phone',
            'description', 'logo_url', 'is_active', 'subscription_plan',
            'subscription_expires_at', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


# PUBLIC_INTERFACE
class CollegeAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for CollegeAdmin model with user and college details.
    """
    user_details = UserSerializer(source='user', read_only=True)
    college_details = CollegeSerializer(source='college', read_only=True)
    
    class Meta:
        model = CollegeAdmin
        fields = [
            'id', 'user', 'college', 'designation', 'department', 'is_primary',
            'permissions', 'created_at', 'updated_at', 'user_details', 'college_details'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


# PUBLIC_INTERFACE
class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for StudentProfile model with comprehensive student information.
    """
    user_details = UserSerializer(source='user', read_only=True)
    college_details = CollegeSerializer(source='college', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'college', 'student_id', 'branch', 'year_of_study',
            'semester', 'current_cgpa', 'total_cgpa', 'date_of_birth', 'gender',
            'category', 'address', 'city', 'state', 'postal_code',
            'emergency_contact_name', 'emergency_contact_phone', 'linkedin_url',
            'github_url', 'portfolio_url', 'skills', 'interests', 'achievements',
            'languages', 'profile_photo_url', 'resume_url', 'is_placement_eligible',
            'placement_status', 'created_at', 'updated_at', 'user_details', 'college_details'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


# PUBLIC_INTERFACE
class JobPostingSerializer(serializers.ModelSerializer):
    """
    Serializer for JobPosting model with job details and application counts.
    """
    college_details = CollegeSerializer(source='college', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'college', 'company_name', 'job_title', 'job_description',
            'job_type', 'location', 'salary_min', 'salary_max', 'currency',
            'required_skills', 'preferred_skills', 'experience_required',
            'education_requirements', 'eligibility_criteria', 'application_deadline',
            'interview_process', 'company_description', 'company_website',
            'company_logo_url', 'contact_person_name', 'contact_person_email',
            'contact_person_phone', 'min_cgpa', 'allowed_branches', 'allowed_years',
            'max_applications', 'status', 'is_featured', 'views_count',
            'applications_count', 'created_at', 'updated_at', 'college_details',
            'created_by_details'
        ]
        extra_kwargs = {
            'views_count': {'read_only': True},
            'applications_count': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


# PUBLIC_INTERFACE
class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for JobApplication model with student and job details.
    """
    student_details = StudentProfileSerializer(source='student', read_only=True)
    job_details = JobPostingSerializer(source='job', read_only=True)
    status_updated_by_details = UserSerializer(source='status_updated_by', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'student', 'cover_letter', 'custom_resume_url',
            'application_data', 'status', 'applied_at', 'status_updated_at',
            'status_updated_by', 'notes', 'score', 'feedback', 'created_at',
            'updated_at', 'student_details', 'job_details', 'status_updated_by_details'
        ]
        extra_kwargs = {
            'applied_at': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


# PUBLIC_INTERFACE
class PlacementRoundSerializer(serializers.ModelSerializer):
    """
    Serializer for PlacementRound model with job details and participant tracking.
    """
    job_details = JobPostingSerializer(source='job', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = PlacementRound
        fields = [
            'id', 'job', 'round_number', 'round_name', 'round_type', 'description',
            'scheduled_at', 'duration_minutes', 'location', 'meeting_link',
            'instructions', 'status', 'max_participants', 'current_participants',
            'created_at', 'updated_at', 'job_details', 'created_by_details'
        ]
        extra_kwargs = {
            'current_participants': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


# PUBLIC_INTERFACE
class PlacementStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for PlacementStatusHistory model with application and user details.
    """
    application_details = JobApplicationSerializer(source='application', read_only=True)
    round_details = PlacementRoundSerializer(source='round', read_only=True)
    changed_by_details = UserSerializer(source='changed_by', read_only=True)
    
    class Meta:
        model = PlacementStatusHistory
        fields = [
            'id', 'application', 'round', 'previous_status', 'new_status',
            'changed_at', 'changed_by', 'reason', 'notes', 'score', 'feedback',
            'application_details', 'round_details', 'changed_by_details'
        ]
        extra_kwargs = {
            'changed_at': {'read_only': True},
        }


# PUBLIC_INTERFACE
class AnalyticsLogSerializer(serializers.ModelSerializer):
    """
    Serializer for AnalyticsLog model with user and college details.
    """
    user_details = UserSerializer(source='user', read_only=True)
    college_details = CollegeSerializer(source='college', read_only=True)
    
    class Meta:
        model = AnalyticsLog
        fields = [
            'id', 'user', 'college', 'event_type', 'event_data', 'ip_address',
            'user_agent', 'session_id', 'created_at', 'user_details', 'college_details'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
        }


# PUBLIC_INTERFACE
class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model with college and creator details.
    """
    college_details = CollegeSerializer(source='college', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'college', 'title', 'message', 'type', 'template_id',
            'template_data', 'target_roles', 'target_users', 'target_criteria',
            'scheduled_at', 'expires_at', 'priority', 'status', 'created_at',
            'updated_at', 'college_details', 'created_by_details'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


# PUBLIC_INTERFACE
class NotificationRecipientSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationRecipient model with notification and user details.
    """
    notification_details = NotificationSerializer(source='notification', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = NotificationRecipient
        fields = [
            'id', 'notification', 'user', 'status', 'sent_at', 'delivered_at',
            'read_at', 'error_message', 'retry_count', 'created_at', 'updated_at',
            'notification_details', 'user_details'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


# PUBLIC_INTERFACE
class DocumentUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for DocumentUpload model with user and college details.
    """
    user_details = UserSerializer(source='user', read_only=True)
    college_details = CollegeSerializer(source='college', read_only=True)
    verified_by_details = UserSerializer(source='verified_by', read_only=True)
    
    class Meta:
        model = DocumentUpload
        fields = [
            'id', 'user', 'college', 'entity_type', 'entity_id', 'document_type',
            'file_name', 'file_path', 'file_size', 'mime_type', 'file_hash',
            'is_public', 'is_verified', 'verified_by', 'verified_at', 'expires_at',
            'metadata', 'created_at', 'updated_at', 'user_details', 'college_details',
            'verified_by_details'
        ]
        extra_kwargs = {
            'file_size': {'read_only': True},
            'file_hash': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


# PUBLIC_INTERFACE
class AuditTrailSerializer(serializers.ModelSerializer):
    """
    Serializer for AuditTrail model with user and college details.
    """
    user_details = UserSerializer(source='user', read_only=True)
    college_details = CollegeSerializer(source='college', read_only=True)
    
    class Meta:
        model = AuditTrail
        fields = [
            'id', 'user', 'college', 'entity_type', 'entity_id', 'action',
            'old_values', 'new_values', 'ip_address', 'user_agent', 'session_id',
            'created_at', 'user_details', 'college_details'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
        }
