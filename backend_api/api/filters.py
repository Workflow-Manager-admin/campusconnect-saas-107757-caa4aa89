import django_filters
from django.db.models import Q
from .models import (
    User, StudentProfile, JobPosting, JobApplication, AnalyticsLog
)


# PUBLIC_INTERFACE
class UserFilter(django_filters.FilterSet):
    """
    Filter for User model with advanced filtering options.
    """
    name = django_filters.CharFilter(method='filter_name')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = User
        fields = ['role', 'is_active', 'email_verified']
    
    def filter_name(self, queryset, name, value):
        """Filter by first name or last name."""
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )


# PUBLIC_INTERFACE
class JobPostingFilter(django_filters.FilterSet):
    """
    Filter for JobPosting model with comprehensive filtering.
    """
    salary_min = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    deadline_after = django_filters.DateTimeFilter(field_name='application_deadline', lookup_expr='gte')
    deadline_before = django_filters.DateTimeFilter(field_name='application_deadline', lookup_expr='lte')
    skills = django_filters.CharFilter(method='filter_skills')
    branches = django_filters.CharFilter(method='filter_branches')
    
    class Meta:
        model = JobPosting
        fields = [
            'college', 'status', 'job_type', 'is_featured', 'company_name',
            'location', 'min_cgpa'
        ]
    
    def filter_skills(self, queryset, name, value):
        """Filter jobs by required or preferred skills."""
        return queryset.filter(
            Q(required_skills__icontains=value) | Q(preferred_skills__icontains=value)
        )
    
    def filter_branches(self, queryset, name, value):
        """Filter jobs by allowed branches."""
        return queryset.filter(allowed_branches__icontains=value)


# PUBLIC_INTERFACE
class StudentProfileFilter(django_filters.FilterSet):
    """
    Filter for StudentProfile model with academic filtering.
    """
    cgpa_min = django_filters.NumberFilter(field_name='current_cgpa', lookup_expr='gte')
    cgpa_max = django_filters.NumberFilter(field_name='current_cgpa', lookup_expr='lte')
    skills = django_filters.CharFilter(method='filter_skills')
    
    class Meta:
        model = StudentProfile
        fields = [
            'college', 'branch', 'year_of_study', 'is_placement_eligible',
            'placement_status', 'gender', 'category'
        ]
    
    def filter_skills(self, queryset, name, value):
        """Filter students by skills."""
        return queryset.filter(skills__icontains=value)


# PUBLIC_INTERFACE
class JobApplicationFilter(django_filters.FilterSet):
    """
    Filter for JobApplication model with status and date filtering.
    """
    applied_after = django_filters.DateTimeFilter(field_name='applied_at', lookup_expr='gte')
    applied_before = django_filters.DateTimeFilter(field_name='applied_at', lookup_expr='lte')
    score_min = django_filters.NumberFilter(field_name='score', lookup_expr='gte')
    score_max = django_filters.NumberFilter(field_name='score', lookup_expr='lte')
    
    class Meta:
        model = JobApplication
        fields = ['job', 'student', 'status', 'job__college', 'job__company_name']


# PUBLIC_INTERFACE
class AnalyticsLogFilter(django_filters.FilterSet):
    """
    Filter for AnalyticsLog model with event and date filtering.
    """
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = AnalyticsLog
        fields = ['event_type', 'college', 'user', 'user__role']
