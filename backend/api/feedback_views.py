from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import SiteFeedback, NewsletterSubscriber, User, Notification
import logging

logger = logging.getLogger(__name__)

# ========== Site Feedback Views ==========
class SiteFeedbackView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            name = request.data.get('name', '').strip()
            email = request.data.get('email', '').strip()
            feedback_type = request.data.get('feedback_type', 'general')
            subject = request.data.get('subject', '').strip()
            message = request.data.get('message', '').strip()
            
            if not all([name, email, subject, message]):
                return Response(
                    {'message': 'All fields are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            feedback = SiteFeedback.objects.create(
                name=name,
                email=email,
                feedback_type=feedback_type,
                subject=subject,
                message=message
            )
            
            # Notify admins
            admins = User.objects.filter(role__in=['admin', 'super_admin'])
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title=f"New {feedback.get_feedback_type_display()}",
                    message=f"New feedback from {name}: {subject}",
                    link="/admin/api/sitefeedback/"
                )
            
            return Response({
                'message': 'Thank you for your feedback! We will review it and get back to you if needed.'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Failed to submit feedback: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to submit feedback. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Newsletter Subscription Views ==========
class NewsletterSubscriptionView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email', '').strip().lower()
            name = request.data.get('name', '').strip()
            
            if not email:
                return Response(
                    {'message': 'Email address is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if already subscribed
            if NewsletterSubscriber.objects.filter(email=email).exists():
                return Response(
                    {'message': 'This email is already subscribed to our newsletter'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            subscriber = NewsletterSubscriber.objects.create(
                email=email,
                name=name,
                is_active=True
            )
            
            # Notify admins
            admins = User.objects.filter(role__in=['admin', 'super_admin'])
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title="New Newsletter Subscription",
                    message=f"New subscriber: {email}",
                    link="/admin/api/newslettersubscriber/"
                )
            
            return Response({
                'message': 'Successfully subscribed to our newsletter! You will receive updates about new opportunities.'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Failed to subscribe to newsletter: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to subscribe. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        try:
            email = request.data.get('email', '').strip().lower()
            
            if not email:
                return Response(
                    {'message': 'Email address is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                subscriber = NewsletterSubscriber.objects.get(email=email)
                subscriber.delete()
                return Response({
                    'message': 'Successfully unsubscribed from newsletter'
                })
            except NewsletterSubscriber.DoesNotExist:
                return Response(
                    {'message': 'Email not found in our subscription list'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Failed to unsubscribe from newsletter: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to unsubscribe. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
