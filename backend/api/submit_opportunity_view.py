from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from .models import Opportunity
import json

@method_decorator(csrf_exempt, name='dispatch')
class SubmitOpportunityView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
            
            # Create opportunity with pending status
            opportunity = Opportunity.objects.create(
                title=data.get('title'),
                description=data.get('description'),
                opportunity_type=data.get('opportunity_type'),
                organization=data.get('organization', ''),
                location=data.get('location', ''),
                deadline=data.get('deadline') if data.get('deadline') else None,
                deadline_type=data.get('deadline_type', 'not_specified'),
                opportunity_link=data.get('opportunity_link', ''),
                status='pending',  # Set to pending for review
                submitter_name=data.get('submitter_name'),
                submitter_email=data.get('submitter_email'),
                is_featured=False,
                created_at=timezone.now()
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Opportunity submitted successfully for review',
                'opportunity_id': opportunity.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error submitting opportunity: {str(e)}'
            }, status=400)
