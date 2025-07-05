from rest_framework import serializers
from .models import (
    User, College, Department, StudentProfile, Company, Job, 
    Application, PlacementRound, RoundParticipation, Placement,
    Notification, SystemConfiguration
)


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer for API responses
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class CollegeSerializer(serializers.ModelSerializer):
    """
    College serializer
    """
    class Meta:
        model = College
        fields = ['id', 'name', 'code', 'address', 'city', 'state', 'country', 'phone', 'email', 'website', 'established_year', 'is_active']
        read_only_fields = ['id']


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Department serializer
    """
    college_name = serializers.CharField(source='college.name', read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'college', 'college_name', 'description', 'is_active']
        read_only_fields = ['id']


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Student profile serializer
    """
    user = UserSerializer(read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'college', 'college_name', 'department', 'department_name',
            'student_id', 'roll_number', 'date_of_birth', 'gender', 'address',
            'city', 'state', 'pincode', 'admission_year', 'graduation_year',
            'current_semester', 'cgpa', 'percentage', 'tenth_board',
            'tenth_percentage', 'tenth_year', 'twelfth_board', 'twelfth_percentage',
            'twelfth_year', 'is_placed', 'placement_ready', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class CompanySerializer(serializers.ModelSerializer):
    """
    Company serializer
    """
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'website', 'company_type', 'industry',
            'headquarters', 'employee_count', 'founded_year', 'is_active'
        ]
        read_only_fields = ['id']


class JobSerializer(serializers.ModelSerializer):
    """
    Job serializer
    """
    company = CompanySerializer(read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    eligible_departments = DepartmentSerializer(many=True, read_only=True)
    application_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'company', 'college', 'college_name', 'title', 'description',
            'job_type', 'location', 'salary_min', 'salary_max', 'currency',
            'min_cgpa', 'min_percentage', 'eligible_departments', 'eligible_batches',
            'required_skills', 'experience_required', 'application_deadline',
            'interview_date', 'joining_date', 'status', 'max_applications',
            'application_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'application_count']
    
    def get_application_count(self, obj):
        return obj.applications.count()


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Application serializer
    """
    job = JobSerializer(read_only=True)
    student = StudentProfileSerializer(read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'student', 'status', 'cover_letter',
            'additional_documents', 'applied_at', 'updated_at'
        ]
        read_only_fields = ['id', 'applied_at', 'updated_at']


class PlacementRoundSerializer(serializers.ModelSerializer):
    """
    Placement round serializer
    """
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company.name', read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PlacementRound
        fields = [
            'id', 'job', 'job_title', 'company_name', 'round_type', 'round_number',
            'title', 'description', 'venue', 'scheduled_date', 'start_time',
            'end_time', 'status', 'participant_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'participant_count']
    
    def get_participant_count(self, obj):
        return obj.participants.count()


class RoundParticipationSerializer(serializers.ModelSerializer):
    """
    Round participation serializer
    """
    round = PlacementRoundSerializer(read_only=True)
    student = StudentProfileSerializer(read_only=True)
    
    class Meta:
        model = RoundParticipation
        fields = [
            'id', 'round', 'student', 'status', 'score', 'feedback',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PlacementSerializer(serializers.ModelSerializer):
    """
    Placement serializer
    """
    student = StudentProfileSerializer(read_only=True)
    job = JobSerializer(read_only=True)
    
    class Meta:
        model = Placement
        fields = [
            'id', 'student', 'job', 'offer_letter', 'salary_offered',
            'currency', 'joining_date', 'status', 'offered_at',
            'accepted_at', 'joined_at', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'offered_at', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """
    Notification serializer
    """
    recipient = UserSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'notification_type', 'title',
            'message', 'is_read', 'is_email_sent', 'is_sms_sent',
            'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'created_at']


class SystemConfigurationSerializer(serializers.ModelSerializer):
    """
    System configuration serializer
    """
    class Meta:
        model = SystemConfiguration
        fields = ['id', 'key', 'value', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# Summary serializers for dashboard/overview endpoints
class JobSummarySerializer(serializers.ModelSerializer):
    """
    Simplified job serializer for listings
    """
    company_name = serializers.CharField(source='company.name', read_only=True)
    application_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company_name', 'job_type', 'location',
            'salary_min', 'salary_max', 'application_deadline',
            'status', 'application_count'
        ]
    
    def get_application_count(self, obj):
        return obj.applications.count()


class StudentSummarySerializer(serializers.ModelSerializer):
    """
    Simplified student serializer for listings
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user_name', 'student_id', 'department_name',
            'cgpa', 'graduation_year', 'is_placed', 'placement_ready'
        ]
