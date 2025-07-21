from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Opportunity
from datetime import datetime
import json

@csrf_exempt
@require_http_methods(["POST"])
def submit_public_opportunity(request):
    try:
        # Get data from POST request
        title = request.POST.get('title')
        description = request.POST.get('description')
        opportunity_type = request.POST.get('opportunity_type')
        organization = request.POST.get('organization', '')
        location = request.POST.get('location', '')
        deadline = request.POST.get('deadline') or None
        deadline_type = request.POST.get('deadline_type', 'not_specified')
        opportunity_link = request.POST.get('opportunity_link', '')
        submitter_name = request.POST.get('submitter_name')
        submitter_email = request.POST.get('submitter_email')
        
        # Validate required fields
        if not all([title, description, opportunity_type, opportunity_link]):
            return JsonResponse({
                'success': False,
                'message': 'Missing required fields: title, description, opportunity type, and opportunity link'
            }, status=400)
        
        # Get or create a system user for public submissions
        User = get_user_model()
        system_user, created = User.objects.get_or_create(
            email='system@youthopportunities.com',
            defaults={
                'first_name': 'System',
                'last_name': 'Public',
                'is_active': True
            }
        )
        
        # Handle deadline timezone
        deadline_aware = None
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
                deadline_aware = timezone.make_aware(datetime.combine(deadline_date, datetime.min.time()))
            except:
                deadline_aware = None
        
        # Auto-subscribe to newsletter if email provided (silent)
        if submitter_email:
            from .models import NewsletterSubscriber
            try:
                subscriber, created = NewsletterSubscriber.objects.get_or_create(
                    email=submitter_email,
                    defaults={'name': submitter_name or ''}
                )
                if created:
                    print(f"Auto-subscribed {submitter_email} to newsletter")
            except Exception as e:
                print(f"Newsletter auto-subscription failed: {e}")
        
        # Create opportunity with pending status
        # Note: submitter info stored in description for admin reference
        if submitter_name or submitter_email:
            submitter_info = f"\n\n--- Submitted by: {submitter_name or 'Anonymous'} ({submitter_email or 'No email provided'}) ---"
            full_description = f"{description}{submitter_info}"
        else:
            full_description = f"{description}\n\n--- Submitted anonymously ---"
        
        opportunity = Opportunity.objects.create(
            title=title,
            description=full_description,
            opportunity_type=opportunity_type,
            organization=organization or '',
            location=location or '',
            deadline=deadline_aware,
            deadline_type=deadline_type,
            opportunity_link=opportunity_link or '',
            status='pending',
            is_featured=False,
            created_by=system_user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Opportunity submitted successfully for review',
            'opportunity_id': opportunity.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)
