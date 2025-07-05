from rest_framework import permissions
from .models import UserRole, CollegeAdmin


# PUBLIC_INTERFACE
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission that allows only owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the owner
        return obj.user == request.user


# PUBLIC_INTERFACE
class IsStudentUser(permissions.BasePermission):
    """
    Permission that allows access only to student users.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == UserRole.STUDENT
        )


# PUBLIC_INTERFACE
class IsCollegeAdminUser(permissions.BasePermission):
    """
    Permission that allows access only to college admin users.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]
        )


# PUBLIC_INTERFACE
class IsSuperAdminUser(permissions.BasePermission):
    """
    Permission that allows access only to super admin users.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == UserRole.SUPER_ADMIN
        )


# PUBLIC_INTERFACE
class IsCollegeAdminOrSuperAdmin(permissions.BasePermission):
    """
    Permission that allows access to college admin or super admin users.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO, UserRole.SUPER_ADMIN]
        )


# PUBLIC_INTERFACE
class IsCollegeMember(permissions.BasePermission):
    """
    Permission that allows access only to users belonging to the same college.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Super admin can access all colleges
        if request.user.role == UserRole.SUPER_ADMIN:
            return True
        
        # Get user's college based on role
        user_college = None
        if request.user.role == UserRole.STUDENT:
            try:
                user_college = request.user.studentprofile.college
            except:
                return False
        elif request.user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            try:
                college_admin = CollegeAdmin.objects.get(user=request.user)
                user_college = college_admin.college
            except:
                return False
        
        # Check if object belongs to the same college
        if hasattr(obj, 'college'):
            return obj.college == user_college
        elif hasattr(obj, 'student') and hasattr(obj.student, 'college'):
            return obj.student.college == user_college
        elif hasattr(obj, 'job') and hasattr(obj.job, 'college'):
            return obj.job.college == user_college
        
        return False


# PUBLIC_INTERFACE
class CanManageJobApplications(permissions.BasePermission):
    """
    Permission that allows students to manage their own applications
    and college admins to manage applications for their college jobs.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Super admin can access all applications
        if request.user.role == UserRole.SUPER_ADMIN:
            return True
        
        # Students can only access their own applications
        if request.user.role == UserRole.STUDENT:
            return obj.student.user == request.user
        
        # College admins can access applications for their college jobs
        if request.user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            try:
                college_admin = CollegeAdmin.objects.get(user=request.user)
                return obj.job.college == college_admin.college
            except:
                return False
        
        return False


# PUBLIC_INTERFACE
class CanManageJobPostings(permissions.BasePermission):
    """
    Permission that allows college admins to manage job postings for their college.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role in [
            UserRole.COLLEGE_ADMIN, UserRole.TPO, UserRole.SUPER_ADMIN
        ]
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Super admin can access all job postings
        if request.user.role == UserRole.SUPER_ADMIN:
            return True
        
        # College admins can only access their college's job postings
        if request.user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            try:
                college_admin = CollegeAdmin.objects.get(user=request.user)
                return obj.college == college_admin.college
            except:
                return False
        
        return False


# PUBLIC_INTERFACE
class CanManageStudentProfiles(permissions.BasePermission):
    """
    Permission that allows students to manage their own profiles
    and college admins to manage students from their college.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Super admin can access all profiles
        if request.user.role == UserRole.SUPER_ADMIN:
            return True
        
        # Students can only access their own profile
        if request.user.role == UserRole.STUDENT:
            return obj.user == request.user
        
        # College admins can access students from their college
        if request.user.role in [UserRole.COLLEGE_ADMIN, UserRole.TPO]:
            try:
                college_admin = CollegeAdmin.objects.get(user=request.user)
                return obj.college == college_admin.college
            except:
                return False
        
        return False
