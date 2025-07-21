from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ServiceRequest, NewsletterSubscriber

@csrf_exempt
@require_http_methods(["POST"])
def submit_service_request(request):
    try:
        # Get data from POST request
        service_type = request.POST.get('service_type')
        name = request.POST.get('name')
        email = request.POST.get('email')
        people_count = request.POST.get('people_count', 1)
        preferred_date = request.POST.get('preferred_date') or None
        description = request.POST.get('description')
        additional_info = request.POST.get('additional_info', '')
        contact_info = request.POST.get('contact_info', '')
        link = request.POST.get('link', '')
        file_upload = request.FILES.get('file_upload')
        
        # Debug print
        print(f"Service Type: {service_type}")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Description: {description}")
        
        # Validate required fields based on service type
        required_fields = [service_type, name, email]
        
        # Only require description for services that have it
        if service_type not in ['cv']:
            required_fields.append(description)
        
        if not all(required_fields):
            missing = []
            if not service_type: missing.append('service type')
            if not name: missing.append('name')
            if not email: missing.append('email')
            if service_type not in ['cv'] and not description: missing.append('description')
            
            return JsonResponse({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing)}'
            }, status=400)
        
        # Auto-subscribe to newsletter if email provided
        if email:
            try:
                NewsletterSubscriber.objects.get_or_create(
                    email=email,
                    defaults={'name': name}
                )
            except Exception as e:
                print(f"Newsletter auto-subscription failed: {e}")
        
        # Create service request
        service_request = ServiceRequest.objects.create(
            service_type=service_type,
            name=name,
            email=email,
            people_count=int(people_count) if people_count else 1,
            preferred_date=preferred_date,
            description=description or f'{service_type.title()} service request',
            additional_info=additional_info,
            contact_info=contact_info,
            link=link,
            file_upload=file_upload,
            status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Service request submitted successfully! We will contact you soon.',
            'request_id': service_request.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)
