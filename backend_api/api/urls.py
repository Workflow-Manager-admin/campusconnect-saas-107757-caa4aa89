from django.urls import path
from .views import health, dashboard_stats, jobs_list, students_list

urlpatterns = [
    path('health/', health, name='Health'),
    path('dashboard/stats/', dashboard_stats, name='DashboardStats'),
    path('jobs/', jobs_list, name='JobsList'),
    path('students/', students_list, name='StudentsList'),
]
