import sys
import os
import time
from django.utils import timezone

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        print("RequestLoggingMiddleware initialized", flush=True)

    def __call__(self, request):
        # Skip static files
        if request.path.startswith('/static/') or request.path.startswith('/admin/jsi18n/'):
            return self.get_response(request)
            
        start_time = time.time()
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Log request details
        print(f"[{timestamp}] {request.method} {request.get_full_path()}", flush=True)
        print(f"User: {getattr(request, 'user', 'Anonymous')}", flush=True)
        print(f"IP: {self.get_client_ip(request)}", flush=True)
        
        response = self.get_response(request)
        
        # Log response details
        end_time = time.time()
        duration = round((end_time - start_time) * 1000, 2)
        
        print(f"Status: {response.status_code} | Duration: {duration}ms", flush=True)
        print("-" * 50, flush=True)
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
