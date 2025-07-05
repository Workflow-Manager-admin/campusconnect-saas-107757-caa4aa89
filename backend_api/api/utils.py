from django.utils import timezone
from .models import CollegeAdmin, StudentProfile, AnalyticsLog


# PUBLIC_INTERFACE
def get_user_college(user):
    """
    Get the college associated with a user based on their role.
    Returns None if user has no associated college.
    """
    if user.role == 'student':
        try:
            return user.studentprofile.college
        except StudentProfile.DoesNotExist:
            return None
    elif user.role in ['college_admin', 'tpo']:
        try:
            college_admin = CollegeAdmin.objects.get(user=user)
            return college_admin.college
        except CollegeAdmin.DoesNotExist:
            return None
    return None


# PUBLIC_INTERFACE
def log_user_activity(user, event_type, event_data=None, request=None):
    """
    Log user activity for analytics tracking.
    """
    if event_data is None:
        event_data = {}
    
    college = get_user_college(user)
    
    analytics_data = {
        'user': user,
        'college': college,
        'event_type': event_type,
        'event_data': event_data,
        'created_at': timezone.now()
    }
    
    if request:
        analytics_data.update({
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'session_id': request.session.session_key if hasattr(request, 'session') else None
        })
    
    return AnalyticsLog.objects.create(**analytics_data)


# PUBLIC_INTERFACE
def check_user_college_access(user, target_college):
    """
    Check if a user has access to resources from a specific college.
    """
    if user.role == 'super_admin':
        return True
    
    user_college = get_user_college(user)
    if user_college and user_college.id == target_college.id:
        return True
    
    return False


# PUBLIC_INTERFACE
def get_college_statistics(college):
    """
    Get comprehensive statistics for a college.
    """
    from django.db.models import Avg
    from .models import JobPosting, JobApplication, StudentProfile
    
    stats = {
        'total_students': StudentProfile.objects.filter(college=college).count(),
        'placement_eligible': StudentProfile.objects.filter(
            college=college, is_placement_eligible=True
        ).count(),
        'placed_students': StudentProfile.objects.filter(
            college=college, placement_status='placed'
        ).count(),
        'active_jobs': JobPosting.objects.filter(
            college=college, status='active'
        ).count(),
        'total_applications': JobApplication.objects.filter(
            job__college=college
        ).count(),
        'average_cgpa': StudentProfile.objects.filter(
            college=college
        ).aggregate(avg_cgpa=Avg('current_cgpa'))['avg_cgpa'] or 0,
    }
    
    # Calculate placement percentage
    if stats['placement_eligible'] > 0:
        stats['placement_percentage'] = (
            stats['placed_students'] / stats['placement_eligible']
        ) * 100
    else:
        stats['placement_percentage'] = 0
    
    return stats


# PUBLIC_INTERFACE
def validate_job_eligibility(student_profile, job_posting):
    """
    Validate if a student is eligible for a job posting.
    """
    errors = []
    
    # Check CGPA requirement
    if job_posting.min_cgpa and student_profile.current_cgpa:
        if student_profile.current_cgpa < job_posting.min_cgpa:
            errors.append(f'CGPA requirement not met. Required: {job_posting.min_cgpa}, Current: {student_profile.current_cgpa}')
    
    # Check branch eligibility
    if job_posting.allowed_branches and student_profile.branch:
        if student_profile.branch not in job_posting.allowed_branches:
            errors.append(f'Branch not eligible. Allowed: {job_posting.allowed_branches}, Current: {student_profile.branch}')
    
    # Check year eligibility
    if job_posting.allowed_years and student_profile.year_of_study:
        if student_profile.year_of_study not in job_posting.allowed_years:
            errors.append(f'Year not eligible. Allowed: {job_posting.allowed_years}, Current: {student_profile.year_of_study}')
    
    # Check placement eligibility
    if not student_profile.is_placement_eligible:
        errors.append('Student is not eligible for placement')
    
    # Check college match
    if student_profile.college.id != job_posting.college.id:
        errors.append('Job is not available for your college')
    
    # Check application deadline
    if job_posting.application_deadline and timezone.now() > job_posting.application_deadline:
        errors.append('Application deadline has passed')
    
    # Check job status
    if job_posting.status != 'active':
        errors.append('Job is not currently active')
    
    return len(errors) == 0, errors


# PUBLIC_INTERFACE
def format_notification_message(template, data):
    """
    Format notification message using template and data.
    """
    try:
        return template.format(**data)
    except KeyError as e:
        return f"Error formatting message: Missing key {e}"
    except Exception as e:
        return f"Error formatting message: {str(e)}"


# PUBLIC_INTERFACE
def get_user_permissions(user):
    """
    Get comprehensive permissions for a user based on their role.
    """
    base_permissions = {
        'can_view_profile': True,
        'can_edit_profile': True,
        'can_view_jobs': False,
        'can_apply_jobs': False,
        'can_manage_jobs': False,
        'can_view_applications': False,
        'can_manage_applications': False,
        'can_view_students': False,
        'can_manage_students': False,
        'can_view_analytics': False,
        'can_manage_college': False,
        'can_manage_users': False,
        'can_send_notifications': False,
        'can_view_audit_trail': False,
    }
    
    if user.role == 'student':
        base_permissions.update({
            'can_view_jobs': True,
            'can_apply_jobs': True,
            'can_view_applications': True,  # Own applications only
        })
    elif user.role in ['college_admin', 'tpo']:
        base_permissions.update({
            'can_view_jobs': True,
            'can_manage_jobs': True,
            'can_view_applications': True,
            'can_manage_applications': True,
            'can_view_students': True,
            'can_manage_students': True,
            'can_view_analytics': True,
            'can_manage_college': True,
            'can_send_notifications': True,
            'can_view_audit_trail': True,
        })
    elif user.role == 'super_admin':
        # Super admin has all permissions
        for key in base_permissions:
            base_permissions[key] = True
        base_permissions['can_manage_users'] = True
    
    return base_permissions
