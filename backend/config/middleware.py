import re
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Other security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # HTTPS enforcement
        if not request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response

class InputSanitizationMiddleware(MiddlewareMixin):
    """Sanitize user inputs to prevent XSS and injection attacks"""
    
    def process_request(self, request):
        if request.method in ['POST', 'PUT', 'PATCH']:
            # Check for malicious patterns
            malicious_patterns = [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'on\w+\s*=',
                r'eval\s*\(',
                r'expression\s*\(',
            ]
            
            # Check POST data
            if hasattr(request, 'POST'):
                for key, value in request.POST.items():
                    for pattern in malicious_patterns:
                        if re.search(pattern, str(value), re.IGNORECASE):
                            return HttpResponseForbidden('Malicious input detected')
            
            # Check JSON data (skip for multipart/form-data)
            if hasattr(request, 'content_type') and request.content_type == 'application/json':
                try:
                    import json
                    body = request.body.decode('utf-8')
                    data = json.loads(body)
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, str):
                                for pattern in malicious_patterns:
                                    if re.search(pattern, value, re.IGNORECASE):
                                        return HttpResponseForbidden('Malicious input detected')
                except:
                    pass
        
        return None

class RateLimitMiddleware(MiddlewareMixin):
    """Basic rate limiting middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}
        super().__init__(get_response)
    
    def process_request(self, request):
        import time
        
        # Skip rate limiting for authenticated users
        # Check session for authentication since user might not be available yet
        if hasattr(request, 'session') and request.session.get('_auth_user_id'):
            return None
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            return None
        
        # Get client IP
        ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Clean old entries
        self.cleanup_old_requests(current_time)
        
        # Check rate limit (100 requests per minute for unauthenticated users)
        if ip in self.requests:
            if len(self.requests[ip]) >= 100:
                return HttpResponseForbidden('Rate limit exceeded')
        else:
            self.requests[ip] = []
        
        # Add current request
        self.requests[ip].append(current_time)
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def cleanup_old_requests(self, current_time):
        # Remove requests older than 1 minute
        for ip in list(self.requests.keys()):
            self.requests[ip] = [
                req_time for req_time in self.requests[ip]
                if current_time - req_time < 60
            ]
            if not self.requests[ip]:
                del self.requests[ip]
