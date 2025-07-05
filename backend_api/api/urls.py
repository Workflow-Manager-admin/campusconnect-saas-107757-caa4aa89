from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    health, register, login, logout,
    UserViewSet, CollegeViewSet, StudentProfileViewSet, JobPostingViewSet,
    JobApplicationViewSet, PlacementRoundViewSet, NotificationViewSet,
    AnalyticsLogViewSet, DocumentUploadViewSet, AuditTrailViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'colleges', CollegeViewSet, basename='college')
router.register(r'students', StudentProfileViewSet, basename='studentprofile')
router.register(r'jobs', JobPostingViewSet, basename='jobposting')
router.register(r'applications', JobApplicationViewSet, basename='jobapplication')
router.register(r'rounds', PlacementRoundViewSet, basename='placementround')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'analytics', AnalyticsLogViewSet, basename='analyticslog')
router.register(r'documents', DocumentUploadViewSet, basename='documentupload')
router.register(r'audit', AuditTrailViewSet, basename='audittrail')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Health check
    path('health/', health, name='health'),
    
    # API endpoints
    path('', include(router.urls)),
]
