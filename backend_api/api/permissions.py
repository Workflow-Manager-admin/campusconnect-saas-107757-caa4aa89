from rest_framework import permissions

class IsStudent(permissions.BasePermission):
    """
    PUBLIC_INTERFACE
    Permission class to allow access only to users with student role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'student'

class IsTPO(permissions.BasePermission):
    """
    PUBLIC_INTERFACE
    Permission class to allow access only to users with TPO role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'tpo'

class IsCollegeAdmin(permissions.BasePermission):
    """
    PUBLIC_INTERFACE
    Permission class to allow access only to users with college admin role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'admin'

class IsSuperAdmin(permissions.BasePermission):
    """
    PUBLIC_INTERFACE
    Permission class to allow access only to users with super admin role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'super_admin'

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    PUBLIC_INTERFACE
    Permission class to allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
