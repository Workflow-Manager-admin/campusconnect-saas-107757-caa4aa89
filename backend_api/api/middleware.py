from .models import AuditLog

class AuditLogMiddleware:
    """
    Middleware to log user actions for auditing purposes.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Log user actions except for GET requests and API docs
            if request.method != 'GET' and not request.path.startswith(('/docs/', '/swagger/', '/redoc/')):
                AuditLog.objects.create(
                    user=request.user,
                    action=request.method.lower(),
                    resource_type=request.path.split('/')[-2] if request.path.split('/')[-1] else request.path.split('/')[-2],
                    resource_id=request.path.split('/')[-1] if request.path.split('/')[-1].isalnum() else None,
                    description=f"{request.method} request to {request.path}",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
        
        return response
