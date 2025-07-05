from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from .models import Job, StudentProfile, College, Application
from .serializers import JobSummarySerializer, StudentSummarySerializer


# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """
    Health check endpoint to verify server and database connectivity
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return Response({
        "message": "Server is up!",
        "database": db_status,
        "status": "healthy"
    })


# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_stats(request):
    """
    Get dashboard statistics for the platform
    """
    try:
        stats = {
            "total_colleges": College.objects.count(),
            "total_students": StudentProfile.objects.count(),
            "total_jobs": Job.objects.count(),
            "total_applications": Application.objects.count(),
            "placed_students": StudentProfile.objects.filter(is_placed=True).count(),
            "active_jobs": Job.objects.filter(status='published').count(),
        }
        return Response(stats)
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([AllowAny])
def jobs_list(request):
    """
    Get list of published jobs
    """
    try:
        jobs = Job.objects.filter(status='published').order_by('-created_at')[:10]
        serializer = JobSummarySerializer(jobs, many=True)
        return Response({
            "jobs": serializer.data,
            "count": jobs.count()
        })
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([AllowAny])
def students_list(request):
    """
    Get list of students
    """
    try:
        students = StudentProfile.objects.select_related('user', 'department').order_by('-created_at')[:10]
        serializer = StudentSummarySerializer(students, many=True)
        return Response({
            "students": serializer.data,
            "count": students.count()
        })
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
