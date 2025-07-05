from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    College, StudentProfile, JobPosting, JobApplication,
    AnalyticsLog, UserRole
)
from .utils import get_college_statistics
from .permissions import IsCollegeAdminOrSuperAdmin


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='get',
    operation_description="Get dashboard statistics for students",
    responses={200: openapi.Response('Dashboard data', schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'applications_count': openapi.Schema(type=openapi.TYPE_INTEGER),
            'active_jobs_count': openapi.Schema(type=openapi.TYPE_INTEGER),
            'profile_completion': openapi.Schema(type=openapi.TYPE_NUMBER),
            'recent_activities': openapi.Schema(type=openapi.TYPE_ARRAY)
        }
    ))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    """Get dashboard statistics for students."""
    user = request.user
    
    if user.role != UserRole.STUDENT:
        return Response({'error': 'Only students can access this endpoint'}, status=403)
    
    try:
        student_profile = user.studentprofile
        college = student_profile.college
        
        # Get student's applications
        applications = JobApplication.objects.filter(student=student_profile)
        
        # Get active jobs for the college
        active_jobs = JobPosting.objects.filter(
            college=college,
            status='active',
            application_deadline__gte=timezone.now()
        )
        
        # Calculate profile completion percentage
        profile_fields = [
            'student_id', 'branch', 'year_of_study', 'current_cgpa',
            'date_of_birth', 'gender', 'phone', 'linkedin_url',
            'skills', 'resume_url'
        ]
        completed_fields = sum(1 for field in profile_fields if getattr(student_profile, field, None))
        profile_completion = (completed_fields / len(profile_fields)) * 100
        
        # Get recent activities
        recent_activities = AnalyticsLog.objects.filter(
            user=user
        ).order_by('-created_at')[:10]
        
        dashboard_data = {
            'applications_count': applications.count(),
            'active_jobs_count': active_jobs.count(),
            'profile_completion': round(profile_completion, 2),
            'placement_status': student_profile.placement_status,
            'applications_by_status': applications.values('status').annotate(count=Count('id')),
            'recent_activities': [
                {
                    'event_type': activity.event_type,
                    'created_at': activity.created_at,
                    'event_data': activity.event_data
                }
                for activity in recent_activities
            ]
        }
        
        return Response(dashboard_data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=400)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='get',
    operation_description="Get dashboard statistics for college admins",
    responses={200: openapi.Response('Dashboard data', schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'students_count': openapi.Schema(type=openapi.TYPE_INTEGER),
            'jobs_count': openapi.Schema(type=openapi.TYPE_INTEGER),
            'applications_count': openapi.Schema(type=openapi.TYPE_INTEGER),
            'placement_stats': openapi.Schema(type=openapi.TYPE_OBJECT)
        }
    ))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCollegeAdminOrSuperAdmin])
def college_admin_dashboard(request):
    """Get dashboard statistics for college admins."""
    user = request.user
    
    if user.role == UserRole.SUPER_ADMIN:
        # Super admin can see all colleges
        colleges = College.objects.all()
        dashboard_data = {
            'total_colleges': colleges.count(),
            'active_colleges': colleges.filter(is_active=True).count(),
            'total_students': StudentProfile.objects.count(),
            'total_jobs': JobPosting.objects.count(),
            'total_applications': JobApplication.objects.count(),
        }
        return Response(dashboard_data)
    
    try:
        from .models import CollegeAdmin
        college_admin = CollegeAdmin.objects.get(user=user)
        college = college_admin.college
        
        # Get college statistics
        stats = get_college_statistics(college)
        
        # Get recent activities
        recent_activities = AnalyticsLog.objects.filter(
            college=college
        ).order_by('-created_at')[:20]
        
        # Get job statistics
        jobs = JobPosting.objects.filter(college=college)
        job_stats = {
            'total_jobs': jobs.count(),
            'active_jobs': jobs.filter(status='active').count(),
            'draft_jobs': jobs.filter(status='draft').count(),
            'closed_jobs': jobs.filter(status='closed').count(),
        }
        
        # Get application statistics
        applications = JobApplication.objects.filter(job__college=college)
        application_stats = {
            'total_applications': applications.count(),
            'pending_applications': applications.filter(status='applied').count(),
            'shortlisted_applications': applications.filter(status='shortlisted').count(),
            'selected_applications': applications.filter(status='selected').count(),
        }
        
        dashboard_data = {
            **stats,
            'job_stats': job_stats,
            'application_stats': application_stats,
            'recent_activities': [
                {
                    'event_type': activity.event_type,
                    'user': activity.user.email if activity.user else 'System',
                    'created_at': activity.created_at,
                    'event_data': activity.event_data
                }
                for activity in recent_activities
            ]
        }
        
        return Response(dashboard_data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=400)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='get',
    operation_description="Get placement statistics and analytics",
    responses={200: openapi.Response('Placement analytics', schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'placement_percentage': openapi.Schema(type=openapi.TYPE_NUMBER),
            'company_wise_stats': openapi.Schema(type=openapi.TYPE_ARRAY),
            'branch_wise_stats': openapi.Schema(type=openapi.TYPE_ARRAY),
            'monthly_trends': openapi.Schema(type=openapi.TYPE_ARRAY)
        }
    ))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCollegeAdminOrSuperAdmin])
def placement_analytics(request):
    """Get detailed placement analytics."""
    user = request.user
    
    try:
        if user.role == UserRole.SUPER_ADMIN:
            # Super admin can see all data
            students = StudentProfile.objects.all()
            applications = JobApplication.objects.all()
            jobs = JobPosting.objects.all()
        else:
            from .models import CollegeAdmin
            college_admin = CollegeAdmin.objects.get(user=user)
            college = college_admin.college
            
            students = StudentProfile.objects.filter(college=college)
            applications = JobApplication.objects.filter(job__college=college)
            jobs = JobPosting.objects.filter(college=college)
        
        # Calculate placement percentage
        total_eligible = students.filter(is_placement_eligible=True).count()
        total_placed = students.filter(placement_status='placed').count()
        placement_percentage = (total_placed / total_eligible * 100) if total_eligible > 0 else 0
        
        # Company-wise statistics
        company_stats = jobs.values('company_name').annotate(
            total_positions=Count('id'),
            applications_received=Count('jobapplication'),
            students_selected=Count('jobapplication', filter=Q(jobapplication__status='selected'))
        ).order_by('-total_positions')[:10]
        
        # Branch-wise statistics
        branch_stats = students.values('branch').annotate(
            total_students=Count('id'),
            eligible_students=Count('id', filter=Q(is_placement_eligible=True)),
            placed_students=Count('id', filter=Q(placement_status='placed'))
        ).order_by('-total_students')
        
        # Monthly trends for the last 6 months
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_trends = []
        
        for i in range(6):
            month_start = six_months_ago + timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            
            month_data = {
                'month': month_start.strftime('%Y-%m'),
                'jobs_posted': jobs.filter(
                    created_at__gte=month_start,
                    created_at__lt=month_end
                ).count(),
                'applications_received': applications.filter(
                    applied_at__gte=month_start,
                    applied_at__lt=month_end
                ).count(),
                'students_placed': applications.filter(
                    status='selected',
                    status_updated_at__gte=month_start,
                    status_updated_at__lt=month_end
                ).count(),
            }
            monthly_trends.append(month_data)
        
        analytics_data = {
            'placement_percentage': round(placement_percentage, 2),
            'total_eligible_students': total_eligible,
            'total_placed_students': total_placed,
            'company_wise_stats': list(company_stats),
            'branch_wise_stats': list(branch_stats),
            'monthly_trends': monthly_trends,
            'top_recruiting_companies': list(
                company_stats.order_by('-students_selected')[:5]
            )
        }
        
        return Response(analytics_data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=400)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='get',
    operation_description="Get recent notifications for the user",
    responses={200: openapi.Response('Recent notifications', schema=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(type=openapi.TYPE_OBJECT)
    ))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_notifications(request):
    """Get recent notifications for the user."""
    user = request.user
    
    try:
        # Get notifications targeted to the user
        from .models import NotificationRecipient
        user_notifications = NotificationRecipient.objects.filter(
            user=user
        ).select_related('notification').order_by('-created_at')[:20]
        
        notifications_data = []
        for recipient in user_notifications:
            notification = recipient.notification
            notifications_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.type,
                'priority': notification.priority,
                'status': recipient.status,
                'sent_at': recipient.sent_at,
                'read_at': recipient.read_at,
                'created_at': notification.created_at,
            })
        
        return Response(notifications_data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=400)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='post',
    operation_description="Mark notification as read",
    responses={200: openapi.Response('Notification marked as read')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    user = request.user
    
    try:
        from .models import NotificationRecipient
        recipient = NotificationRecipient.objects.get(
            notification_id=notification_id,
            user=user
        )
        
        recipient.read_at = timezone.now()
        recipient.save()
        
        return Response({'message': 'Notification marked as read'})
        
    except NotificationRecipient.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
