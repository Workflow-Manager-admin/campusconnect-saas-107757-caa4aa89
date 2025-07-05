from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from .filters import (
    UserFilter, JobPostingFilter, StudentProfileFilter, 
    JobApplicationFilter, AnalyticsLogFilter
)
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from django.db.models import Q, Count, Avg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    User, College, CollegeAdmin, StudentProfile, JobPosting, JobApplication,
    PlacementRound, PlacementStatusHistory, AnalyticsLog, Notification,
    DocumentUpload, AuditTrail, UserRole, ApplicationStatus
)
from .serializers import (
    UserSerializer, UserLoginSerializer, CollegeSerializer,
    StudentProfileSerializer, JobPostingSerializer, JobApplicationSerializer,
    PlacementRoundSerializer, AnalyticsLogSerializer,
    NotificationSerializer, DocumentUploadSerializer,
    AuditTrailSerializer
)
from .permissions import (
    IsCollegeAdminOrSuperAdmin, CanManageJobApplications, CanManageJobPostings,
    CanManageStudentProfiles
)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='get',
    operation_description="Health check endpoint to verify API status",
    responses={200: openapi.Response('API is healthy', schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
    ))}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """Health check endpoint to verify API status."""
    return Response({"message": "Server is up!"})


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='post',
    operation_description="Register a new user account",
    request_body=UserSerializer,
    responses={201: UserSerializer, 400: 'Bad Request'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user account with role-based validation."""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Log analytics event
        AnalyticsLog.objects.create(
            user=user,
            event_type='user_registration',
            event_data={'role': user.role},
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
        )
        
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='post',
    operation_description="Login user and return JWT tokens",
    request_body=UserLoginSerializer,
    responses={200: openapi.Response('Login successful', schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'access': openapi.Schema(type=openapi.TYPE_STRING),
            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
            'user': openapi.Schema(type=openapi.TYPE_OBJECT)
        }
    ))}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user and return JWT tokens."""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Update last login
        user.last_login = timezone.now()
        user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Log analytics event
        AnalyticsLog.objects.create(
            user=user,
            event_type='login',
            event_data={'role': user.role},
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
        )
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='post',
    operation_description="Logout user and blacklist refresh token",
    responses={200: openapi.Response('Logout successful')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user and blacklist refresh token."""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Log analytics event
        AnalyticsLog.objects.create(
            user=request.user,
            event_type='logout',
            event_data={'role': request.user.role},
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
        )
        
        return Response({'message': 'Logout successful'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users with role-based access control.
    Provides CRUD operations for user management.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'last_login']
    
    def get_queryset(self):
        """Filter users based on role permissions."""
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return User.objects.all()
        elif user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            # College admins can see users from their college
            try:
                college_admin = CollegeAdmin.objects.get(user=user)
                college = college_admin.college
                # Get all users from the same college
                college_users = User.objects.filter(
                    Q(studentprofile__college=college) |
                    Q(collegeadmin__college=college)
                ).distinct()
                return college_users
            except CollegeAdmin.DoesNotExist:
                return User.objects.none()
        else:
            # Students can only see their own profile
            return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change user password."""
        user = self.get_object()
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not check_password(old_password, user.password_hash):
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.password_hash = make_password(new_password)
        user.save()
        
        return Response({'message': 'Password changed successfully'})


# PUBLIC_INTERFACE
class CollegeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing colleges with role-based access control.
    """
    serializer_class = CollegeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'subscription_plan', 'state', 'country']
    search_fields = ['name', 'code', 'city']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        """Filter colleges based on role permissions."""
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return College.objects.all()
        elif user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            # College admins can only see their own college
            try:
                college_admin = CollegeAdmin.objects.get(user=user)
                return College.objects.filter(id=college_admin.college.id)
            except CollegeAdmin.DoesNotExist:
                return College.objects.none()
        else:
            # Students can see their college
            try:
                return College.objects.filter(id=user.studentprofile.college.id)
            except:
                return College.objects.none()


# PUBLIC_INTERFACE
class StudentProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student profiles with comprehensive filtering.
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated, CanManageStudentProfiles]
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentProfileFilter
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'student_id']
    ordering_fields = ['created_at', 'current_cgpa', 'year_of_study']
    
    def get_queryset(self):
        """Filter student profiles based on role permissions."""
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return StudentProfile.objects.all()
        elif user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            # College admins can see students from their college
            try:
                college_admin = CollegeAdmin.objects.get(user=user)
                return StudentProfile.objects.filter(college=college_admin.college)
            except CollegeAdmin.DoesNotExist:
                return StudentProfile.objects.none()
        else:
            # Students can only see their own profile
            try:
                return StudentProfile.objects.filter(user=user)
            except:
                return StudentProfile.objects.none()
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get student statistics for the college."""
        queryset = self.get_queryset()
        stats = {
            'total_students': queryset.count(),
            'placement_eligible': queryset.filter(is_placement_eligible=True).count(),
            'placed_students': queryset.filter(placement_status='placed').count(),
            'average_cgpa': queryset.aggregate(avg_cgpa=Avg('current_cgpa'))['avg_cgpa'],
            'branch_wise': queryset.values('branch').annotate(count=Count('id')),
            'year_wise': queryset.values('year_of_study').annotate(count=Count('id')),
        }
        return Response(stats)


# PUBLIC_INTERFACE
class JobPostingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job postings with advanced filtering and search.
    """
    serializer_class = JobPostingSerializer
    permission_classes = [IsAuthenticated, CanManageJobPostings]
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobPostingFilter
    search_fields = ['job_title', 'company_name', 'location', 'required_skills']
    ordering_fields = ['created_at', 'application_deadline', 'salary_min']
    
    def get_queryset(self):
        """Filter job postings based on role permissions."""
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return JobPosting.objects.all()
        elif user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            # College admins can see jobs from their college
            try:
                college_admin = CollegeAdmin.objects.get(user=user)
                return JobPosting.objects.filter(college=college_admin.college)
            except CollegeAdmin.DoesNotExist:
                return JobPosting.objects.none()
        else:
            # Students can see active jobs from their college
            try:
                return JobPosting.objects.filter(
                    college=user.studentprofile.college,
                    status='active'
                )
            except:
                return JobPosting.objects.none()
    
    def perform_create(self, serializer):
        """Set the creator and college when creating a job posting."""
        if self.request.user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            college_admin = CollegeAdmin.objects.get(user=self.request.user)
            serializer.save(
                created_by=self.request.user,
                college=college_admin.college
            )
        else:
            serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply for a job posting."""
        job = self.get_object()
        
        if request.user.role != UserRole.STUDENT:
            return Response({'error': 'Only students can apply for jobs'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            student = request.user.studentprofile
        except:
            return Response({'error': 'Student profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Check if already applied
        if JobApplication.objects.filter(job=job, student=student).exists():
            return Response({'error': 'Already applied for this job'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create application
        application = JobApplication.objects.create(
            job=job,
            student=student,
            cover_letter=request.data.get('cover_letter', ''),
            custom_resume_url=request.data.get('custom_resume_url', ''),
            application_data=request.data.get('application_data', {})
        )
        
        # Update job application count
        job.applications_count += 1
        job.save()
        
        # Log analytics event
        AnalyticsLog.objects.create(
            user=request.user,
            college=student.college,
            event_type='job_apply',
            event_data={'job_id': str(job.id), 'job_title': job.job_title},
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
        )
        
        return Response(JobApplicationSerializer(application).data, 
                       status=status.HTTP_201_CREATED)


# PUBLIC_INTERFACE
class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job applications with status tracking.
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated, CanManageJobApplications]
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobApplicationFilter
    search_fields = ['student__user__first_name', 'student__user__last_name', 'job__job_title']
    ordering_fields = ['applied_at', 'status_updated_at', 'score']
    
    def get_queryset(self):
        """Filter applications based on role permissions."""
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return JobApplication.objects.all()
        elif user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            # College admins can see applications for their college jobs
            try:
                college_admin = CollegeAdmin.objects.get(user=user)
                return JobApplication.objects.filter(job__college=college_admin.college)
            except CollegeAdmin.DoesNotExist:
                return JobApplication.objects.none()
        else:
            # Students can only see their own applications
            try:
                return JobApplication.objects.filter(student__user=user)
            except:
                return JobApplication.objects.none()
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update application status with history tracking."""
        application = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in [choice[0] for choice in ApplicationStatus.choices]:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create status history
        PlacementStatusHistory.objects.create(
            application=application,
            previous_status=application.status,
            new_status=new_status,
            changed_by=request.user,
            reason=request.data.get('reason', ''),
            notes=request.data.get('notes', ''),
            score=request.data.get('score'),
            feedback=request.data.get('feedback', '')
        )
        
        # Update application
        application.status = new_status
        application.status_updated_at = timezone.now()
        application.status_updated_by = request.user
        application.notes = request.data.get('notes', application.notes)
        application.score = request.data.get('score', application.score)
        application.feedback = request.data.get('feedback', application.feedback)
        application.save()
        
        return Response(JobApplicationSerializer(application).data)


# PUBLIC_INTERFACE
class PlacementRoundViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing placement rounds with scheduling and participant tracking.
    """
    serializer_class = PlacementRoundSerializer
    permission_classes = [IsAuthenticated, IsCollegeAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['job', 'round_type', 'status', 'job__college']
    search_fields = ['round_name', 'job__job_title', 'job__company_name']
    ordering_fields = ['scheduled_at', 'round_number']
    
    def get_queryset(self):
        """Filter placement rounds based on role permissions."""
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return PlacementRound.objects.all()
        elif user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            try:
                college_admin = CollegeAdmin.objects.get(user=user)
                return PlacementRound.objects.filter(job__college=college_admin.college)
            except CollegeAdmin.DoesNotExist:
                return PlacementRound.objects.none()
        else:
            return PlacementRound.objects.none()
    
    def perform_create(self, serializer):
        """Set the creator when creating a placement round."""
        serializer.save(created_by=self.request.user)


# PUBLIC_INTERFACE
class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications with role-based targeting.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsCollegeAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['college', 'type', 'status', 'priority']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'scheduled_at', 'priority']
    
    def get_queryset(self):
        """Filter notifications based on role permissions."""
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return Notification.objects.all()
        elif user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            try:
                college_admin = CollegeAdmin.objects.get(user=user)
                return Notification.objects.filter(college=college_admin.college)
            except CollegeAdmin.DoesNotExist:
                return Notification.objects.none()
        else:
            return Notification.objects.none()
    
    def perform_create(self, serializer):
        """Set the creator and college when creating a notification."""
        if self.request.user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            college_admin = CollegeAdmin.objects.get(user=self.request.user)
            serializer.save(
                created_by=self.request.user,
                college=college_admin.college
            )
        else:
            serializer.save(created_by=self.request.user)


# PUBLIC_INTERFACE
class AnalyticsLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing analytics logs with filtering and aggregation.
    """
    serializer_class = AnalyticsLogSerializer
    permission_classes = [IsAuthenticated, IsCollegeAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AnalyticsLogFilter
    search_fields = ['event_type', 'user__email']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        """Filter analytics logs based on role permissions."""
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return AnalyticsLog.objects.all()
        elif user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            try:
                college_admin = CollegeAdmin.objects.get(user=user)
                return AnalyticsLog.objects.filter(college=college_admin.college)
            except CollegeAdmin.DoesNotExist:
                return AnalyticsLog.objects.none()
        else:
            return AnalyticsLog.objects.none()
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get analytics summary for the college."""
        queryset = self.get_queryset()
        summary = {
            'total_events': queryset.count(),
            'event_types': queryset.values('event_type').annotate(count=Count('id')),
            'daily_activity': queryset.extra(
                select={'day': 'date(created_at)'}
            ).values('day').annotate(count=Count('id')).order_by('day'),
            'user_activity': queryset.values('user__role').annotate(count=Count('id')),
        }
        return Response(summary)


# PUBLIC_INTERFACE
class DocumentUploadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document uploads with verification tracking.
    """
    serializer_class = DocumentUploadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document_type', 'is_verified', 'is_public', 'college']
    search_fields = ['file_name', 'user__email']
    ordering_fields = ['created_at', 'verified_at']
    
    def get_queryset(self):
        """Filter documents based on role permissions."""
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return DocumentUpload.objects.all()
        elif user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            try:
                college_admin = CollegeAdmin.objects.get(user=user)
                return DocumentUpload.objects.filter(college=college_admin.college)
            except CollegeAdmin.DoesNotExist:
                return DocumentUpload.objects.none()
        else:
            # Students can only see their own documents
            return DocumentUpload.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """Set the user and college when creating a document."""
        college = None
        if self.request.user.role == UserRole.STUDENT:
            try:
                college = self.request.user.studentprofile.college
            except:
                pass
        elif self.request.user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            try:
                college_admin = CollegeAdmin.objects.get(user=self.request.user)
                college = college_admin.college
            except:
                pass
        
        serializer.save(user=self.request.user, college=college)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a document (college admins only)."""
        document = self.get_object()
        
        if request.user.role not in [UserRole.COLLEGE_ADMIN, UserRole.TPO, UserRole.SUPER_ADMIN]:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        document.is_verified = True
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.save()
        
        return Response(DocumentUploadSerializer(document).data)


# PUBLIC_INTERFACE
class AuditTrailViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit trails with comprehensive filtering.
    """
    serializer_class = AuditTrailSerializer
    permission_classes = [IsAuthenticated, IsCollegeAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entity_type', 'action', 'user', 'college']
    search_fields = ['entity_type', 'action', 'user__email']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        """Filter audit trails based on role permissions."""
        user = self.request.user
        if user.role == UserRole.SUPER_ADMIN:
            return AuditTrail.objects.all()
        elif user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            try:
                college_admin = CollegeAdmin.objects.get(user=user)
                return AuditTrail.objects.filter(college=college_admin.college)
            except CollegeAdmin.DoesNotExist:
                return AuditTrail.objects.none()
        else:
            return AuditTrail.objects.none()
