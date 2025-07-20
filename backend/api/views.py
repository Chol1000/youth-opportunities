from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from functools import reduce
import logging
import os
import re
from urllib.parse import unquote

from .models import (
    User, Education, Experience, UserDocument,
    Opportunity, Notification, MentorRequest, MentorshipSession,
    Feedback, Advertisement, CollaborationRequest, TrainingSession,
    TrainingRegistration, Report, CVReview, ApplicationGuidance,
    InterviewPreparation, ProfileOptimization, SuccessTip, Webinar,
    WebinarRegistration, CommunityPost, PostComment, PostReaction,
    ServiceRequest, BlogPost, SuccessStory, MentorApplication, InternalDiscussion, InternalDiscussionReply,
    ChatRoom, ChatMessage
)
from django.utils import timezone
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, 
    ProfileUpdateSerializer, EducationSerializer, ExperienceSerializer,
    UserDocumentSerializer, OpportunitySerializer, NotificationSerializer,
    MentorRequestSerializer, MentorshipSessionSerializer, FeedbackSerializer,
    AdvertisementSerializer, CollaborationRequestSerializer, TrainingSessionSerializer,
    TrainingRegistrationSerializer, ReportSerializer, CVReviewSerializer,
    ApplicationGuidanceSerializer, InterviewPreparationSerializer, 
    ProfileOptimizationSerializer, SuccessTipSerializer, WebinarSerializer,
    WebinarRegistrationSerializer, UserRoleUpdateSerializer, BanUserSerializer,
    CommunityPostSerializer, PostCommentSerializer, PostReactionSerializer,
    CommunityPostCreateSerializer, MentorApplicationSerializer, InternalDiscussionSerializer, InternalDiscussionReplySerializer
)

logger = logging.getLogger(__name__)

# ========== Authentication Views ==========
class CSRFTokenView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return JsonResponse({'csrfToken': get_token(request)})

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Input validation and sanitization
        data = request.data.copy()
        
        # Sanitize text inputs
        for field in ['first_name', 'last_name', 'email']:
            if field in data:
                data[field] = re.sub(r'<[^>]*>', '', str(data[field])).strip()
        
        # Email validation
        if 'email' in data and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', data['email']):
            return Response(
                {'message': 'Invalid email format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RegisterSerializer(data=data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = serializer.save()
            user.role = 'super_admin' if user.email == 'cholnaroh@gmail.com' else 'user'
            user.is_active = True
            user.save()
            
            self.send_welcome_email(user)
            return Response({
                'message': 'Registration successful! Redirecting to login...',
                'redirect': '/login.html'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Registration failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Registration failed. Please try again.', 'errors': {'non_field_errors': [str(e)]}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def send_welcome_email(self, user):
        try:
            subject = "Welcome to Our Platform!"
            message = render_to_string('emails/welcome_email.html', {
                'user': user,
                'login_url': settings.FRONTEND_LOGIN_URL
            })
            send_mail(subject, "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
            
            if not check_password(password, user.password):
                return Response(
                    {'message': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if user.is_banned_now:
                return Response(
                    {'message': 'Your account has been banned. ' + 
                     (f"Reason: {user.ban_reason}" if user.ban_reason else "") +
                     (f" Until: {user.ban_until.strftime('%Y-%m-%d')}" if user.ban_until else "")},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if user exists but is inactive (for reactivation)
            if not user.is_active:
                user.is_active = True
                user.save()
                
                # Create notification for reactivation
                Notification.objects.create(
                    user=user,
                    title="Account Reactivated",
                    message="Welcome back! Your account has been reactivated successfully.",
                    link="/user_dashboard/notifications.html"
                )
            
            # Authenticate and login
            user = authenticate(request, username=email, password=password)
            if user is not None:
                # Account already reactivated above if needed
                
                login(request, user)
                response = Response({
                    'message': 'Login successful',
                    'user': UserSerializer(user).data,
                    'redirect': '/admin_dashboard/index.html' if user.is_admin() else '/user_dashboard/profile.html'
                })
                
                # Set session cookie attributes
                request.session.save()
                response.set_cookie(
                    'sessionid', 
                    request.session.session_key, 
                    httponly=True,
                    secure=settings.SESSION_COOKIE_SECURE,
                    samesite='Lax'
                )
                return response
            else:
                return Response(
                    {'message': 'Authentication failed'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except User.DoesNotExist:
            return Response(
                {'message': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Login failed. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = f"{settings.FRONTEND_BASE_URL}/reset_password.html?uid={uid}&token={token}"
            
            subject = "Password Reset Request"
            message = render_to_string('emails/reset_password.html', {
                'user': user,
                'reset_url': reset_url
            })
            
            send_mail(subject, "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message)
            
            return Response({'message': 'If this email exists, a reset link has been sent'})
        except ObjectDoesNotExist:
            return Response({'message': 'If this email exists, a reset link has been sent'})
        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to process password reset'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        uid = request.data.get('uid')
        new_password = request.data.get('newPassword')
        confirm_password = request.data.get('confirmPassword')

        if not all([token, uid, new_password, confirm_password]):
            return Response({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'message': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            
            if not default_token_generator.check_token(user, token):
                return Response({'message': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
                
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset successfully'})
            
        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to reset password'},
                status=status.HTTP_400_BAD_REQUEST
            )

# ========== Profile Management Views ==========
class UpdateProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ProfileUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': UserSerializer(user).data
            })
        except Exception as e:
            logger.error(f"Profile update failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update profile'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserPreferencesView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            preferences = request.user.preferences or {}
            return Response({
                'preferences': preferences
            })
        except Exception as e:
            logger.error(f"Failed to get user preferences: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to get preferences'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        try:
            request.user.preferences = request.data
            request.user.save()
            return Response({
                'message': 'Preferences saved successfully'
            })
        except Exception as e:
            logger.error(f"Failed to save preferences: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to save preferences'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OpportunityMatchingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            preferences = user.preferences or {}
            opportunity_types = preferences.get('opportunity_types', [])
            
            if not opportunity_types:
                return Response({'matches': []})
            
            # Base query for opportunities
            query = Q(status='approved')
            
            # Add filters based on opportunity types
            type_queries = []
            for opp_type in opportunity_types:
                type_queries.append(Q(opportunity_type=opp_type))
            
            query &= reduce(lambda x, y: x | y, type_queries)
            
            # Add specific filters for each opportunity type
            if 'scholarship' in opportunity_types:
                scholarship_prefs = preferences.get('scholarship', {})
                scholarship_query = Q()
                
                if scholarship_prefs.get('level'):
                    scholarship_query &= Q(subtype=scholarship_prefs['level'])
                if scholarship_prefs.get('type'):
                    scholarship_query &= Q(additional_filters__contains={'funding_type': scholarship_prefs['type']})
                if scholarship_prefs.get('location'):
                    scholarship_query &= Q(additional_filters__contains={'location': scholarship_prefs['location']})
                if scholarship_prefs.get('field'):
                    scholarship_query &= Q(description__icontains=scholarship_prefs['field'])
                
                query &= scholarship_query
            
            if 'job' in opportunity_types:
                job_prefs = preferences.get('job', {})
                job_query = Q()
                
                if job_prefs.get('type'):
                    job_query &= Q(subtype=job_prefs['type'])
                if job_prefs.get('industry'):
                    job_query &= Q(description__icontains=job_prefs['industry'])
                if job_prefs.get('location'):
                    job_query &= Q(location__icontains=job_prefs['location'])
                if job_prefs.get('experience'):
                    job_query &= Q(additional_filters__contains={'experience_level': job_prefs['experience']})
                
                query &= job_query
            
            if 'internship' in opportunity_types:
                internship_prefs = preferences.get('internship', {})
                internship_query = Q()
                
                if internship_prefs.get('duration'):
                    internship_query &= Q(additional_filters__contains={'duration': internship_prefs['duration']})
                if internship_prefs.get('field'):
                    internship_query &= Q(description__icontains=internship_prefs['field'])
                if internship_prefs.get('paid'):
                    internship_query &= Q(additional_filters__contains={'compensation': internship_prefs['paid']})
                
                query &= internship_query
            
            # Get matching opportunities
            matching_opportunities = Opportunity.objects.filter(query).order_by('-created_at')[:10]
            serializer = OpportunitySerializer(matching_opportunities, many=True)
            
            return Response({
                'matches': serializer.data
            })
        except Exception as e:
            logger.error(f"Failed to find matching opportunities: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to find matching opportunities'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EducationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        educations = Education.objects.filter(user=request.user)
        serializer = EducationSerializer(educations, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = EducationSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            education = serializer.save(user=request.user)
            return Response(EducationSerializer(education).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Education creation failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create education record'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EducationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk, user):
        try:
            return Education.objects.get(pk=pk, user=user)
        except Education.DoesNotExist:
            return None
    
    def get(self, request, pk):
        education = self.get_object(pk, request.user)
        if not education:
            return Response({'message': 'Education record not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EducationSerializer(education)
        return Response(serializer.data)
    
    def put(self, request, pk):
        education = self.get_object(pk, request.user)
        if not education:
            return Response({'message': 'Education record not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EducationSerializer(education, data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            education = serializer.save()
            return Response(EducationSerializer(education).data)
        except Exception as e:
            logger.error(f"Education update failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update education record'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk):
        education = self.get_object(pk, request.user)
        if not education:
            return Response({'message': 'Education record not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            education.delete()
            return Response({'message': 'Education record deleted successfully'})
        except Exception as e:
            logger.error(f"Education deletion failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to delete education record'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExperienceView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        experiences = Experience.objects.filter(user=request.user)
        serializer = ExperienceSerializer(experiences, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ExperienceSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            experience = serializer.save(user=request.user)
            return Response(ExperienceSerializer(experience).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Experience creation failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create experience record'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExperienceDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk, user):
        try:
            return Experience.objects.get(pk=pk, user=user)
        except Experience.DoesNotExist:
            return None
    
    def get(self, request, pk):
        experience = self.get_object(pk, request.user)
        if not experience:
            return Response({'message': 'Experience record not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExperienceSerializer(experience)
        return Response(serializer.data)
    
    def put(self, request, pk):
        experience = self.get_object(pk, request.user)
        if not experience:
            return Response({'message': 'Experience record not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExperienceSerializer(experience, data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            experience = serializer.save()
            return Response(ExperienceSerializer(experience).data)
        except Exception as e:
            logger.error(f"Experience update failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update experience record'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk):
        experience = self.get_object(pk, request.user)
        if not experience:
            return Response({'message': 'Experience record not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            experience.delete()
            return Response({'message': 'Experience record deleted successfully'})
        except Exception as e:
            logger.error(f"Experience deletion failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to delete experience record'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {'message': 'Both current and new password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.check_password(current_password):
            return Response(
                {'message': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            request.user.set_password(new_password)
            request.user.save()
            # Update session to prevent logout
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            
            # Create notification for password change
            Notification.objects.create(
                user=request.user,
                title="Password Changed Successfully",
                message="Your account password has been updated.",
                link="/user_dashboard/notifications.html"
            )
            
            return Response({'message': 'Password changed successfully'})
        except Exception as e:
            logger.error(f"Password change failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to change password'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DeactivateAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.is_active = False
            request.user.save()
            logout(request)
            return Response({'message': 'Account deactivated successfully'})
        except Exception as e:
            logger.error(f"Account deactivation failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to deactivate account'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        password = request.data.get('password')

        if not password:
            return Response(
                {'message': 'Password is required to confirm account deletion'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.check_password(password):
            return Response(
                {'message': 'Incorrect password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_id = request.user.id
            
            # Delete related data first to avoid foreign key constraints
            from django.db import connection
            with connection.cursor() as cursor:
                # Delete from tables that reference the user
                tables_to_clean = [
                    'api_notification', 'api_userdocument', 'api_education', 'api_experience',
                    'api_mentorrequest', 'api_mentorshipsession', 'api_feedback', 'api_report',
                    'api_cvreview', 'api_trainingregistration', 'api_webinarregistration',
                    'api_communitypost', 'api_postcomment', 'api_postreaction',
                    'api_chatmessage', 'api_opportunity'
                ]
                
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                
                for table in tables_to_clean:
                    try:
                        cursor.execute(f"DELETE FROM {table} WHERE user_id = %s", [user_id])
                    except:
                        pass
                
                # Delete chat room participants
                try:
                    cursor.execute("DELETE FROM api_chatroom_participants WHERE user_id = %s", [user_id])
                except:
                    pass
                
                # Delete from the correct user table
                try:
                    cursor.execute("DELETE FROM api_user WHERE id = %s", [user_id])
                except:
                    pass
                
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            # User is already deleted above
            
            logout(request)
            return Response({'message': 'Account deleted successfully'})
        except Exception as e:
            logger.error(f"Account deletion failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to delete account'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Document Management Views ==========
class UserDocumentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            documents = UserDocument.objects.filter(user=request.user).order_by('-uploaded_at')
            serializer = UserDocumentSerializer(documents, many=True, context={'request': request})
            return Response({
                'documents': serializer.data,
                'count': documents.count()
            })
        except Exception as e:
            logger.error(f"Failed to fetch documents: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch documents'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        # Check if file exists in the request
        if 'file' not in request.FILES:
            return Response(
                {'message': 'No file was uploaded'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        data = request.data.copy()
        data['user'] = request.user.id
        
        serializer = UserDocumentSerializer(
            data=data, 
            context={'request': request}
        )
        
        if not serializer.is_valid():
            logger.error(f"Document validation failed: {serializer.errors}")
            return Response(
                {'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            document = serializer.save()
            return Response(
                UserDocumentSerializer(document, context={'request': request}).data, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Document upload failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to upload document', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserDocumentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk, user):
        try:
            return UserDocument.objects.get(pk=pk, user=user)
        except UserDocument.DoesNotExist:
            return None
    
    def get(self, request, pk):
        document = self.get_object(pk, request.user)
        if not document:
            return Response(
                {'message': 'Document not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserDocumentSerializer(document, context={'request': request})
        return Response(serializer.data)
    
    def delete(self, request, pk):
        document = self.get_object(pk, request.user)
        if not document:
            return Response(
                {'message': 'Document not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Delete the file from storage
            if document.file:
                document.file.delete(save=False)
            # Delete the database record
            document.delete()
            return Response(
                {'message': 'Document deleted successfully'}
            )
        except Exception as e:
            logger.error(f"Document deletion failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to delete document'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Opportunity Views ==========
class OpportunityView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        try:
            opportunity_type = request.query_params.get('type')
            status_filter = request.query_params.get('status')
            opportunities = Opportunity.objects.all()

            if opportunity_type:
                opportunities = opportunities.filter(opportunity_type=opportunity_type)
            
            if status_filter and status_filter != 'all':
                opportunities = opportunities.filter(status=status_filter)
            elif not status_filter:
                opportunities = opportunities.filter(status='approved')
            # If status_filter == 'all', don't filter by status

            serializer = OpportunitySerializer(
                opportunities.order_by('-created_at'),
                many=True,
                context={'request': request}
            )
            return Response({
                'opportunities': serializer.data,
                'total': opportunities.count()
            })
        except Exception as e:
            logger.error(f"Opportunity listing failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to load opportunities'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CreateOpportunityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        
        serializer = OpportunitySerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(
                {'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            opportunity = serializer.save(created_by=request.user)
            
            if request.user.role in ['admin', 'super_admin']:
                opportunity.status = 'approved'
                opportunity.save()
                
                # Notify all users about new opportunity
                from django.contrib.auth import get_user_model
                User = get_user_model()
                users = User.objects.filter(is_active=True).exclude(id=request.user.id)
                for user in users:
                    Notification.objects.create(
                        user=user,
                        title=f"New {opportunity.get_opportunity_type_display()} Available",
                        message=f"A new {opportunity.get_opportunity_type_display().lower()} '{opportunity.title}' has been added.",
                        link=f"/user_dashboard/opportunities.html"
                    )
            
            return Response({
                'message': 'Opportunity created successfully',
                'opportunity': OpportunitySerializer(opportunity, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Opportunity creation failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create opportunity'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OpportunityDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, opportunity_id):
        try:
            opportunity = get_object_or_404(Opportunity, id=opportunity_id, status='approved')
            
            # Increment view count
            opportunity.views_count += 1
            opportunity.save(update_fields=['views_count'])
            
            serializer = OpportunitySerializer(opportunity, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch opportunity details: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch opportunity details'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateOpportunityStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, opportunity_id):
        if not request.user.is_admin():
            return Response(
                {'message': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        opportunity = get_object_or_404(Opportunity, id=opportunity_id)
        new_status = request.data.get('status')
        
        if new_status not in ['approved', 'rejected']:
            return Response(
                {'message': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            opportunity.status = new_status
            opportunity.save()
            
            Notification.objects.create(
                user=opportunity.created_by,
                title=f"Your opportunity '{opportunity.title}' has been {new_status}",
                message=f"The opportunity you submitted titled '{opportunity.title}' has been {new_status} by the admin.",
                link=f"/user_dashboard/opportunities.html"
            )
            
            # If approved, notify all users about new opportunity
            if new_status == 'approved':
                from django.contrib.auth import get_user_model
                User = get_user_model()
                users = User.objects.filter(is_active=True).exclude(id=opportunity.created_by.id)
                for user in users:
                    Notification.objects.create(
                        user=user,
                        title=f"New {opportunity.get_opportunity_type_display()} Available",
                        message=f"A new {opportunity.get_opportunity_type_display().lower()} '{opportunity.title}' has been approved.",
                        link=f"/user_dashboard/opportunities.html"
                    )
            
            return Response({
                'message': f'Opportunity has been {new_status}',
                'opportunity': OpportunitySerializer(opportunity, context={'request': request}).data
            })
        except Exception as e:
            logger.error(f"Opportunity status update failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update opportunity status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Notification Views ==========
class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
            unread_count = notifications.filter(is_read=False).count()
            
            serializer = NotificationSerializer(notifications, many=True)
            return Response({
                'notifications': serializer.data,
                'unread_count': unread_count
            })
        except Exception as e:
            logger.error(f"Failed to fetch notifications: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch notifications'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MarkNotificationAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'message': 'Notification marked as read'})
        except Notification.DoesNotExist:
            return Response(
                {'message': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to mark notification as read'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MarkAllNotificationsAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            return Response({'message': 'All notifications marked as read'})
        except Exception as e:
            logger.error(f"Failed to mark all notifications as read: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to mark all notifications as read'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Mentor Views ==========
class MentorListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            # Return active users with mentor role
            mentors = User.objects.filter(role='mentor', is_active=True).order_by('-date_joined')
            serializer = UserSerializer(mentors, many=True, context={'request': request})
            
            return Response({
                'mentors': serializer.data,
                'total_count': mentors.count()
            })
        except Exception as e:
            logger.error(f"Failed to fetch mentors: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch mentors'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Mentorship Views ==========
class MentorRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            request_type = request.query_params.get('type')
            status_filter = request.query_params.get('status')
            
            if request_type == 'sent':
                requests = MentorRequest.objects.filter(mentee=request.user).select_related('mentor')
            elif request_type == 'received':
                requests = MentorRequest.objects.filter(mentor=request.user).select_related('mentee')
            elif status_filter:
                requests = MentorRequest.objects.filter(
                    Q(mentee=request.user) | Q(mentor=request.user),
                    status=status_filter
                ).select_related('mentor', 'mentee')
            else:
                requests = MentorRequest.objects.filter(
                    Q(mentee=request.user) | Q(mentor=request.user)
                ).select_related('mentor', 'mentee')
            
            requests = requests.order_by('-created_at')
            serializer = MentorRequestSerializer(requests, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch mentor requests: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch mentor requests'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        try:
            mentor_id = request.data.get('mentor_id')
            if not mentor_id:
                return Response(
                    {'message': 'Mentor ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            mentor = User.objects.get(id=mentor_id, role='mentor')
            
            # Check if request already exists
            existing_request = MentorRequest.objects.filter(
                mentee=request.user,
                mentor=mentor
            ).first()
            
            if existing_request:
                if existing_request.status == 'pending':
                    return Response(
                        {'message': 'You already have a pending request with this mentor'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                elif existing_request.status == 'approved':
                    return Response(
                        {'message': 'You are already connected with this mentor'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                elif existing_request.status == 'rejected':
                    # Allow new request if previous was rejected
                    existing_request.delete()
            
            mentor_request = MentorRequest.objects.create(
                mentee=request.user,
                mentor=mentor,
                topic='Connection Request',
                message='Connection request sent',
                status='pending'
            )
            
            Notification.objects.create(
                user=mentor,
                title=f"New connection request from {request.user.full_name}",
                message=f"{request.user.full_name} wants to connect with you as a mentor",
                link=f"/mentorship/requests/{mentor_request.id}"
            )
            
            return Response({
                'message': 'Connection request sent successfully',
                'request': MentorRequestSerializer(mentor_request).data
            }, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                {'message': 'Mentor not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Failed to create mentor request: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create mentor request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MentorRequestDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, request_id):
        try:
            mentor_request = get_object_or_404(MentorRequest, id=request_id)
            
            # Allow deletion if user is mentee (cancel request) or mentor (disconnect)
            if request.user not in [mentor_request.mentee, mentor_request.mentor]:
                return Response(
                    {'message': 'Not authorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            mentor_request.delete()
            
            if request.user == mentor_request.mentee:
                message = 'Request cancelled successfully'
            else:
                message = 'Disconnected from mentee successfully'
            
            return Response({'message': message})
        except Exception as e:
            logger.error(f"Failed to delete mentor request: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to process request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateMentorRequestStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, request_id):
        mentor_request = get_object_or_404(MentorRequest, id=request_id, mentor=request.user)
        new_status = request.data.get('status')
        
        if new_status not in ['approved', 'rejected']:
            return Response(
                {'message': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            mentor_request.status = new_status
            mentor_request.save()
            
            Notification.objects.create(
                user=mentor_request.mentee,
                title=f"Mentorship Request {new_status.title()}",
                message=f"Your mentorship request has been {new_status} by {request.user.full_name}.",
                link="/user_dashboard/mentors.html"
            )
            
            # Don't automatically create sessions - let users schedule them manually
            
            return Response({
                'message': f'Connection request has been {new_status}',
                'request': MentorRequestSerializer(mentor_request).data
            })
        except Exception as e:
            logger.error(f"Failed to update mentor request status: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update mentor request status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MentorshipSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            upcoming = request.query_params.get('upcoming', 'false').lower() == 'true'
            pending = request.query_params.get('pending', 'false').lower() == 'true'
            sessions = MentorshipSession.objects.filter(
                Q(mentor=request.user) | Q(mentee=request.user)).select_related('mentor', 'mentee')
            
            if pending:
                # Show sessions with pending status
                sessions = sessions.filter(
                    is_completed=False,
                    status='pending'
                ).order_by('scheduled_time')
            elif upcoming:
                # Show approved sessions that haven't ended yet (start + duration)
                from django.db.models import F
                from django.utils import timezone
                import datetime as dt
                
                now = timezone.now()
                sessions = sessions.filter(
                    is_completed=False,
                    status='approved'
                ).extra(
                    where=["scheduled_time + INTERVAL duration MINUTE > %s"],
                    params=[now]
                ).order_by('scheduled_time')
            else:
                # For completed/previous sessions - approved sessions that have ended
                completed = request.query_params.get('completed', 'false').lower() == 'true'
                if completed:
                    from django.utils import timezone
                    now = timezone.now()
                    sessions = sessions.filter(
                        status='approved'
                    ).extra(
                        where=["scheduled_time + INTERVAL duration MINUTE <= %s"],
                        params=[now]
                    ).order_by('-scheduled_time')
                else:
                    sessions = sessions.filter(
                        status='approved'
                    ).extra(
                        where=["scheduled_time + INTERVAL duration MINUTE <= %s"],
                        params=[now]
                    ).order_by('-scheduled_time')
            
            serializer = MentorshipSessionSerializer(sessions, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch mentorship sessions: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch mentorship sessions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, session_id):
        try:
            session = get_object_or_404(MentorshipSession, id=session_id)
            
            if request.user not in [session.mentor, session.mentee]:
                return Response(
                    {'message': 'Not authorized to edit this session'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Allow editing pending and approved sessions
            if session.status not in ['pending', 'approved']:
                return Response(
                    {'message': 'Only pending and approved sessions can be edited'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update session fields
            if 'preferred_date' in request.data and 'preferred_time' in request.data:
                scheduled_datetime = datetime.strptime(
                    f"{request.data['preferred_date']} {request.data['preferred_time']}", 
                    "%Y-%m-%d %H:%M"
                )
                session.scheduled_time = scheduled_datetime
            
            if 'duration' in request.data:
                session.duration = request.data['duration']
            
            if 'meeting_link' in request.data:
                session.meeting_link = request.data['meeting_link']
            
            if 'notes' in request.data:
                session.notes = request.data['notes']
            
            # Update session status if provided
            if 'status' in request.data:
                session.status = request.data['status']
            
            # Handle decline reason
            if 'decline_reason' in request.data:
                session.decline_reason = request.data['decline_reason']
            
            session.save()
            
            return Response({
                'message': 'Session updated successfully',
                'session': MentorshipSessionSerializer(session, context={'request': request}).data
            })
        except Exception as e:
            logger.error(f"Failed to update session: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, session_id):
        try:
            session = get_object_or_404(MentorshipSession, id=session_id)
            
            if request.user not in [session.mentor, session.mentee]:
                return Response(
                    {'message': 'Not authorized to cancel this session'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            session.delete()
            return Response({'message': 'Session cancelled successfully'})
        except Exception as e:
            logger.error(f"Failed to cancel session: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to cancel session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MentorshipSessionRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            mentor_request_id = request.data.get('mentor_request_id')
            mentor_request = get_object_or_404(MentorRequest, id=mentor_request_id, status='approved')
            
            # Check for existing pending sessions only
            existing_session = MentorshipSession.objects.filter(
                mentor=mentor_request.mentor,
                mentee=request.user,
                is_completed=False,
                status='pending'
            ).first()
            
            if existing_session:
                return Response(
                    {'message': 'You cannot request another session until a decision is made on your current session request'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Combine date and time
            preferred_date = request.data.get('preferred_date')
            preferred_time = request.data.get('preferred_time')
            scheduled_datetime = datetime.strptime(f"{preferred_date} {preferred_time}", "%Y-%m-%d %H:%M")
            
            # Use provided meeting link, don't generate default (keep empty for pending)
            meeting_link = request.data.get('meeting_link', '')
            
            session = MentorshipSession.objects.create(
                mentor=mentor_request.mentor,
                mentee=mentor_request.mentee,
                request=mentor_request,
                scheduled_time=scheduled_datetime,
                duration=request.data.get('duration', 60),
                notes=request.data.get('notes', ''),
                meeting_link=meeting_link,
                status='pending'
            )
            
            # Notify mentor
            Notification.objects.create(
                user=mentor_request.mentor,
                title=f"New session request from {request.user.full_name}",
                message=f"Session requested for {scheduled_datetime.strftime('%Y-%m-%d at %H:%M')}. Topic: {request.data.get('topic', 'Session')}",
                link=f"/user_dashboard/mentors.html"
            )
            
            return Response({
                'message': 'Session request sent successfully',
                'session': MentorshipSessionSerializer(session, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to create session request: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create session request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    


# ========== Feedback Views ==========
class FeedbackView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            feedbacks = Feedback.objects.filter(is_public=True).order_by('-created_at')
            serializer = FeedbackSerializer(feedbacks, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch feedbacks: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch feedbacks'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            feedback = serializer.save(user=request.user)
            return Response({
                'message': 'Feedback submitted successfully',
                'feedback': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to submit feedback: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to submit feedback'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Advertisement Views ==========
class AdvertisementView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        try:
            ads = Advertisement.objects.filter(
                is_active=True,
                start_date__lte=datetime.now(),
                end_date__gte=datetime.now()
            ).order_by('-created_at')
            
            serializer = AdvertisementSerializer(ads, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch advertisements: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch advertisements'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CreateAdvertisementView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.is_admin():
            return Response(
                {'message': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AdvertisementSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            ad = serializer.save(created_by=request.user)
            return Response({
                'message': 'Advertisement created successfully',
                'advertisement': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Advertisement creation failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create advertisement'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Collaboration Views ==========
class CollaborationRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin():
            return Response(
                {'message': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            status_filter = request.query_params.get('status', 'pending')
            requests = CollaborationRequest.objects.filter(status=status_filter).order_by('-created_at')
            serializer = CollaborationRequestSerializer(requests, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch collaboration requests: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch collaboration requests'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        serializer = CollaborationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            request = serializer.save(requester=request.user)
            
            admins = User.objects.filter(role__in=['admin', 'super_admin'])
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title="New collaboration request",
                    message=f"A new collaboration request has been submitted by {request.requester.full_name} from {request.organization_name}.",
                    link=f"/collaborations/{request.id}"
                )
            
            return Response({
                'message': 'Collaboration request submitted successfully',
                'request': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to submit collaboration request: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to submit collaboration request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateCollaborationRequestStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        if not request.user.is_admin():
            return Response(
                {'message': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        collab_request = get_object_or_404(CollaborationRequest, id=request_id)
        new_status = request.data.get('status')
        
        if new_status not in ['approved', 'rejected']:
            return Response(
                {'message': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            collab_request.status = new_status
            collab_request.save()
            
            Notification.objects.create(
                user=collab_request.requester,
                title=f"Your collaboration request has been {new_status}",
                message=f"Your collaboration request with {collab_request.organization_name} has been {new_status}.",
                link=f"/collaborations/{collab_request.id}"
            )
            
            return Response({
                'message': f'Collaboration request has been {new_status}',
                'request': CollaborationRequestSerializer(collab_request).data
            })
        except Exception as e:
            logger.error(f"Failed to update collaboration request status: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update collaboration request status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Training Views ==========
class TrainingSessionView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        try:
            # Return all active sessions regardless of time
            sessions = TrainingSession.objects.filter(is_active=True).order_by('start_time')
            serializer = TrainingSessionSerializer(sessions, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch training sessions: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch training sessions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MyTrainingRegistrationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            registrations = TrainingRegistration.objects.filter(user=request.user).select_related('session', 'session__trainer')
            serializer = TrainingRegistrationSerializer(registrations, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch training registrations: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch training registrations'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegisterForTrainingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, session_id):
        session = get_object_or_404(TrainingSession, id=session_id, is_active=True)
        
        registrations_count = TrainingRegistration.objects.filter(session=session).count()
        if registrations_count >= session.max_participants:
            return Response(
                {'message': 'This training session is full'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if TrainingRegistration.objects.filter(user=request.user, session=session).exists():
            return Response(
                {'message': 'You are already registered for this session'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            registration = TrainingRegistration.objects.create(
                user=request.user,
                session=session
            )
            
            Notification.objects.create(
                user=session.trainer,
                title=f"New registration for {session.title}",
                message=f"{request.user.full_name} has registered for your training session '{session.title}'.",
                link=f"/user_dashboard/training.html"
            )
            
            # Notify user about successful registration
            Notification.objects.create(
                user=request.user,
                title="Training Registration Confirmed",
                message=f"You have successfully registered for '{session.title}'.",
                link="/user_dashboard/training.html"
            )
            
            return Response({
                'message': 'Registered for training session successfully',
                'registration': TrainingRegistrationSerializer(registration).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to register for training session: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to register for training session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UnregisterFromTrainingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, session_id):
        try:
            registration = get_object_or_404(TrainingRegistration, user=request.user, session_id=session_id)
            registration.delete()
            
            return Response({
                'message': 'Successfully cancelled registration'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to cancel registration: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to cancel registration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MyWebinarRegistrationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            registrations = WebinarRegistration.objects.filter(user=request.user).select_related('webinar', 'webinar__presenter')
            serializer = WebinarRegistrationSerializer(registrations, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch webinar registrations: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch webinar registrations'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegisterForWebinarView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, webinar_id):
        try:
            webinar = get_object_or_404(Webinar, id=webinar_id, is_active=True)
            
            # Check if already registered
            if WebinarRegistration.objects.filter(user=request.user, webinar=webinar).exists():
                return Response(
                    {'message': 'You are already registered for this webinar'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create registration
            registration = WebinarRegistration.objects.create(
                user=request.user,
                webinar=webinar
            )
            
            return Response({
                'message': 'Successfully registered for webinar',
                'registration_id': registration.id
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to register for webinar: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to register for webinar'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UnregisterFromWebinarView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, webinar_id):
        try:
            registration = get_object_or_404(WebinarRegistration, user=request.user, webinar_id=webinar_id)
            registration.delete()
            
            return Response({
                'message': 'Successfully cancelled registration'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to cancel webinar registration: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to cancel registration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Report Views ==========
class ReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin():
            return Response(
                {'message': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            status_filter = request.query_params.get('status', 'open')
            reports = Report.objects.filter(status=status_filter).order_by('-created_at')
            serializer = ReportSerializer(reports, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch reports: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch reports'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            report = serializer.save(reporter=request.user)
            
            admins = User.objects.filter(role__in=['admin', 'super_admin'])
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title=f"New {report.get_report_type_display()}",
                    message=f"A new {report.get_report_type_display().lower()} has been submitted by {request.user.full_name}.",
                    link=f"/reports/{report.id}"
                )
            
            return Response({
                'message': 'Report submitted successfully',
                'report': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to submit report: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to submit report'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateReportStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, report_id):
        if not request.user.is_admin():
            return Response(
                {'message': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        report = get_object_or_404(Report, id=report_id)
        new_status = request.data.get('status')
        admin_notes = request.data.get('admin_notes', '')
        
        if new_status not in ['in_progress', 'resolved', 'rejected']:
            return Response(
                {'message': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            report.status = new_status
            report.admin_notes = admin_notes
            report.save()
            
            Notification.objects.create(
                user=report.reporter,
                title=f"Your report status updated",
                message=f"The status of your report has been updated to {new_status.replace('_', ' ')}.",
                link=f"/reports/{report.id}"
            )
            
            return Response({
                'message': f'Report status has been updated to {new_status.replace("_", " ")}',
                'report': ReportSerializer(report).data
            })
        except Exception as e:
            logger.error(f"Failed to update report status: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update report status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== CV Review Views ==========
class CVReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            if request.user.is_admin():
                status_filter = request.query_params.get('status', 'pending')
                reviews = CVReview.objects.filter(status=status_filter).order_by('-submitted_at')
            else:
                reviews = CVReview.objects.filter(user=request.user).order_by('-submitted_at')
            
            serializer = CVReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch CV reviews: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch CV reviews'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        serializer = CVReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.utils import timezone
            cv_review = serializer.save(user=request.user, submitted_at=timezone.now())
            
            admins = User.objects.filter(role__in=['admin', 'super_admin'])
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title="New CV for review",
                    message=f"{request.user.full_name} has submitted a CV for review.",
                    link=f"/admin/api/cvreview/{cv_review.id}/change/"
                )
            
            # Notify user about submission
            Notification.objects.create(
                user=request.user,
                title="CV Submitted for Review",
                message="Your CV has been submitted successfully and is under review.",
                link="/user_dashboard/cv-review.html"
            )
            
            return Response({
                'message': 'CV submitted for review successfully',
                'review': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to submit CV for review: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to submit CV for review'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateCVReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, review_id):
        if not request.user.is_admin():
            return Response(
                {'message': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        cv_review = get_object_or_404(CVReview, id=review_id)
        serializer = CVReviewSerializer(cv_review, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            updated_review = serializer.save(reviewed_by=request.user, status='completed')
            
            Notification.objects.create(
                user=cv_review.user,
                title="Your CV Review is Complete",
                message=f"Your CV has been reviewed by {request.user.full_name}. Score: {cv_review.score}/100",
                link="/user_dashboard/notifications.html"
            )
            
            return Response({
                'message': 'CV review updated successfully',
                'review': serializer.data
            })
        except Exception as e:
            logger.error(f"Failed to update CV review: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update CV review'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Application Guidance Views ==========
class ApplicationGuidanceView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        try:
            guidance = ApplicationGuidance.objects.all().order_by('-created_at')
            serializer = ApplicationGuidanceSerializer(guidance, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch application guidance: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch application guidance'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Interview Preparation Views ==========
class InterviewPreparationView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        try:
            preparations = InterviewPreparation.objects.all().order_by('-created_at')
            serializer = InterviewPreparationSerializer(preparations, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch interview preparations: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch interview preparations'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Profile Optimization Views ==========
class ProfileOptimizationView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        try:
            optimizations = ProfileOptimization.objects.all().order_by('-created_at')
            serializer = ProfileOptimizationSerializer(optimizations, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch profile optimizations: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch profile optimizations'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Success Tip Views ==========
class SuccessTipView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        try:
            tips = SuccessTip.objects.all().order_by('-created_at')
            serializer = SuccessTipSerializer(tips, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch success tips: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch success tips'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Webinar Views ==========
class WebinarView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        try:
            webinars = Webinar.objects.filter(is_active=True).select_related('presenter').order_by('start_time')
            serializer = WebinarSerializer(webinars, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch webinars: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch webinars'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegisterForWebinarView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, webinar_id):
        webinar = get_object_or_404(Webinar, id=webinar_id, is_active=True)
        
        if WebinarRegistration.objects.filter(user=request.user, webinar=webinar).exists():
            return Response(
                {'message': 'You are already registered for this webinar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            registration = WebinarRegistration.objects.create(
                user=request.user,
                webinar=webinar
            )
            
            Notification.objects.create(
                user=webinar.presenter,
                title=f"New registration for {webinar.title}",
                message=f"{request.user.full_name} has registered for your webinar '{webinar.title}'.",
                link=f"/user_dashboard/webinars.html"
            )
            
            # Notify user about successful registration
            Notification.objects.create(
                user=request.user,
                title="Webinar Registration Confirmed",
                message=f"You have successfully registered for '{webinar.title}'.",
                link="/user_dashboard/webinars.html"
            )
            
            return Response({
                'message': 'Registered for webinar successfully',
                'registration': WebinarRegistrationSerializer(registration).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to register for webinar: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to register for webinar'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class WebinarRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            registrations = WebinarRegistration.objects.filter(user=request.user)
            serializer = WebinarRegistrationSerializer(registrations, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch webinar registrations: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch webinar registrations'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Community Views ==========
class CommunityPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Changed from IsAuthenticatedOrReadOnly
    
    def get(self, request):
        try:
            posts = CommunityPost.objects.all().order_by('-created_at')
            serializer = CommunityPostSerializer(
                posts, 
                many=True, 
                context={'request': request}
            )
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch community posts: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch community posts'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        serializer = CommunityPostCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(
                {'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            post = serializer.save(user=request.user)
            return Response(
                CommunityPostSerializer(post, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Failed to create post: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create post'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CommunityPostDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, post_id):
        try:
            return CommunityPost.objects.get(id=post_id)
        except CommunityPost.DoesNotExist:
            return None
    
    def put(self, request, post_id):
        post = self.get_object(post_id)
        if not post:
            return Response(
                {'message': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if post.user != request.user and not request.user.is_admin():
            return Response(
                {'message': 'You can only edit your own posts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CommunityPostCreateSerializer(
            post, 
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(
                {'message': 'Validation failed', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            updated_post = serializer.save()
            return Response(
                CommunityPostSerializer(updated_post, context={'request': request}).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Failed to update post: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update post'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, post_id):
        post = self.get_object(post_id)
        if not post:
            return Response(
                {'message': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if post.user != request.user and not request.user.is_admin():
            return Response(
                {'message': 'You can only delete your own posts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            post.delete()
            return Response(
                {'message': 'Post deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            logger.error(f"Failed to delete post: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to delete post'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PostCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_post(self, post_id):
        try:
            return CommunityPost.objects.get(id=post_id)
        except CommunityPost.DoesNotExist:
            return None
    
    def post(self, request, post_id):
        post = self.get_post(post_id)
        if not post:
            return Response(
                {'message': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PostCommentSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            comment = serializer.save(post=post, user=request.user)
            
            # Create notification for post owner
            if post.user != request.user:
                Notification.objects.create(
                    user=post.user,
                    title="New comment on your post",
                    message=f"{request.user.full_name} commented on your post",
                    link="/user_dashboard/community.html"
                )
            
            # Create notification for parent comment owner if it's a reply
            if comment.parent_comment and comment.parent_comment.user != request.user:
                Notification.objects.create(
                    user=comment.parent_comment.user,
                    title="New reply to your comment",
                    message=f"{request.user.full_name} replied to your comment",
                    link="/user_dashboard/community.html"
                )
            
            return Response(
                PostCommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Failed to create comment: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create comment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PostReactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_post(self, post_id):
        try:
            return CommunityPost.objects.get(id=post_id)
        except CommunityPost.DoesNotExist:
            return None
    
    def post(self, request, post_id):
        post = self.get_post(post_id)
        if not post:
            return Response(
                {'message': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        reaction_type = request.data.get('reaction_type', 'like')
        
        try:
            # Check if user already reacted to this post
            existing_reaction = PostReaction.objects.filter(
                post=post,
                user=request.user
            ).first()
            
            if existing_reaction:
                # Remove reaction (toggle like)
                existing_reaction.delete()
                return Response(
                    {'message': 'Reaction removed', 'reaction': None},
                    status=status.HTTP_200_OK
                )
            else:
                # Create new reaction (like only)
                reaction = PostReaction.objects.create(
                    post=post,
                    user=request.user
                )
                
                # Create notification for post owner
                if post.user != request.user:
                    Notification.objects.create(
                        user=post.user,
                        title=f"Someone liked your post",
                        message=f"{request.user.full_name} liked your post",
                        link="/user_dashboard/community.html"
                    )
                
                return Response(
                    PostReactionSerializer(reaction).data,
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            logger.error(f"Failed to process reaction: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to process reaction'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== User Profile Views ==========
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch user profile: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch user profile'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserActivityView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            request.user.last_login = timezone.now()
            request.user.save(update_fields=['last_login'])
            return Response({'status': 'updated'})
        except Exception as e:
            logger.error(f"Failed to update user activity: {str(e)}", exc_info=True)
            return Response({'status': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileViewTrackingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            target_user_id = request.data.get('target_user_id')
            if not target_user_id:
                return Response({'status': 'target_user_id_required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if this user already viewed this profile recently (within 1 hour)
            cache_key = f"profile_view_{request.user.id}_{target_user_id}"
            from django.core.cache import cache
            
            if cache.get(cache_key):
                return Response({'status': 'already_counted'})
            
            target_user = User.objects.get(id=target_user_id)
            # Increment profile views count
            target_user.profile_views = (target_user.profile_views or 0) + 1
            target_user.save(update_fields=['profile_views'])
            
            # Set cache for 1 hour to prevent duplicate counts
            cache.set(cache_key, True, 3600)  # 3600 seconds = 1 hour
            
            return Response({'status': 'profile_view_recorded'})
        except User.DoesNotExist:
            return Response({'status': 'user_not_found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to record profile view: {str(e)}", exc_info=True)
            return Response({'status': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========== User Management Views ==========
class UserManagementView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin():
            return Response(
                {'message': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            role_filter = request.query_params.get('role')
            users = User.objects.all()
            
            if role_filter:
                users = users.filter(role=role_filter)
            
            serializer = UserSerializer(users.order_by('-date_joined'), many=True)
            return Response({
                'users': serializer.data,
                'total': users.count()
            })
        except Exception as e:
            logger.error(f"User listing failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to load users'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UsersListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            users = User.objects.exclude(id=request.user.id).filter(is_active=True).order_by('first_name', 'last_name')
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Users listing failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to load users'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ChatRoomView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            rooms = ChatRoom.objects.filter(participants=request.user).order_by('-updated_at')
            room_data = []
            for room in rooms:
                other_participant = room.participants.exclude(id=request.user.id).first()
                last_message = room.messages.last()
                room_data.append({
                    'id': room.id,
                    'participant': UserSerializer(other_participant).data if other_participant else None,
                    'last_message': {
                        'content': last_message.content if last_message else '',
                        'created_at': last_message.created_at if last_message else room.created_at,
                        'sender': last_message.sender.full_name if last_message else ''
                    },
                    'updated_at': room.updated_at
                })
            return Response(room_data)
        except Exception as e:
            logger.error(f"Chat rooms listing failed: {str(e)}", exc_info=True)
            return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            participant_id = request.data.get('participant_id')
            if not participant_id:
                return Response({'message': 'Participant ID required'}, status=status.HTTP_400_BAD_REQUEST)
            
            participant = User.objects.get(id=participant_id)
            
            # Check if room already exists
            existing_room = ChatRoom.objects.filter(
                participants=request.user
            ).filter(
                participants=participant
            ).first()
            
            if existing_room:
                return Response({'room_id': existing_room.id})
            
            # Create new room with explicit field values
            from django.utils import timezone
            room = ChatRoom(created_at=timezone.now(), updated_at=timezone.now())
            room.save()
            room.participants.add(request.user, participant)
            
            return Response({'room_id': room.id}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Chat room creation failed: {str(e)}", exc_info=True)
            return Response({'message': 'Failed to create chat room'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id, participants=request.user)
            messages = room.messages.all().order_by('created_at')
            
            # Mark messages as read for the current user
            messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
            
            message_data = []
            for message in messages:
                message_data.append({
                    'id': message.id,
                    'content': message.content,  # Content is encrypted in DB
                    'sender': {
                        'id': message.sender.id,
                        'full_name': message.sender.full_name,
                        'profile_pic': message.sender.profile_pic.url if message.sender.profile_pic else None
                    },
                    'is_read': message.is_read,
                    'created_at': message.created_at
                })
            return Response(message_data)
        except ChatRoom.DoesNotExist:
            return Response({'message': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Messages listing failed: {str(e)}", exc_info=True)
            return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id, participants=request.user)
            content = request.data.get('content', '').strip()
            
            if not content:
                return Response({'message': 'Message content required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Store encrypted content
            message = ChatMessage.objects.create(
                room=room,
                sender=request.user,
                content=content,  # Content is already encrypted from frontend
                is_read=False
            )
            
            room.updated_at = message.created_at
            room.save()
            
            # Notify other participants
            other_participants = room.participants.exclude(id=request.user.id)
            for participant in other_participants:
                Notification.objects.create(
                    user=participant,
                    title="New Message",
                    message=f"{request.user.full_name} sent you a message",
                    link="/user_dashboard/inbox.html"
                )
            
            return Response({
                'id': message.id,
                'content': message.content,
                'sender': {
                    'id': message.sender.id,
                    'full_name': message.sender.full_name,
                    'profile_pic': message.sender.profile_pic.url if message.sender.profile_pic else None
                },
                'is_read': message.is_read,
                'created_at': message.created_at
            }, status=status.HTTP_201_CREATED)
        except ChatRoom.DoesNotExist:
            return Response({'message': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Message creation failed: {str(e)}", exc_info=True)
            return Response({'message': 'Failed to send message'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, room_id, message_id=None):
        try:
            room = ChatRoom.objects.get(id=room_id, participants=request.user)
            message = ChatMessage.objects.get(id=message_id, room=room, sender=request.user)
            
            content = request.data.get('content', '').strip()
            if not content:
                return Response({'message': 'Message content required'}, status=status.HTTP_400_BAD_REQUEST)
            
            message.content = content
            message.save()
            
            return Response({'message': 'Message updated successfully'}, status=status.HTTP_200_OK)
        except (ChatRoom.DoesNotExist, ChatMessage.DoesNotExist):
            return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Message update failed: {str(e)}", exc_info=True)
            return Response({'message': 'Failed to update message'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, room_id, message_id=None):
        try:
            room = ChatRoom.objects.get(id=room_id, participants=request.user)
            message = ChatMessage.objects.get(id=message_id, room=room, sender=request.user)
            
            message.delete()
            return Response({'message': 'Message deleted successfully'}, status=status.HTTP_200_OK)
        except (ChatRoom.DoesNotExist, ChatMessage.DoesNotExist):
            return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Message deletion failed: {str(e)}", exc_info=True)
            return Response({'message': 'Failed to delete message'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatRoomDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, user_id):
        try:
            participant = User.objects.get(id=user_id)
            room = ChatRoom.objects.filter(
                participants=request.user
            ).filter(
                participants=participant
            ).first()
            
            if room:
                room.delete()
                return Response({'message': 'Conversation deleted successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Conversation deletion failed: {str(e)}", exc_info=True)
            return Response({'message': 'Failed to delete conversation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateUserRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        if not request.user.is_super_admin():
            return Response(
                {'message': 'Super admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = get_object_or_404(User, id=user_id)
        
        if user.email == 'cholnaroh@gmail.com' and request.user.email != 'cholnaroh@gmail.com':
            return Response(
                {'message': 'This super admin cannot be modified'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserRoleUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_role = serializer.validated_data['role']
            
            if new_role == 'super_admin' and request.user.email != 'cholnaroh@gmail.com':
                return Response(
                    {'message': 'Only the primary super admin can create other super admins'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            old_role = user.role
            user.role = new_role
            
            if new_role in ['admin', 'super_admin']:
                user.is_staff = True
            else:
                user.is_staff = False
            
            user.save()
            
            Notification.objects.create(
                user=user,
                title=f"Your role has been updated",
                message=f"Your role has been changed from {old_role} to {new_role} by {request.user.full_name}.",
                link="/profile"
            )
            
            return Response({
                'message': f'User role updated to {new_role}',
                'user': UserSerializer(user).data
            })
        except Exception as e:
            logger.error(f"User role update failed: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update user role'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BanUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        if not request.user.is_admin():
            return Response(
                {'message': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = get_object_or_404(User, id=user_id)
        
        if user.is_super_admin() and not request.user.is_super_admin():
            return Response(
                {'message': 'Only super admin can ban other super admins'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.email == 'cholnaroh@gmail.com':
            return Response(
                {'message': 'This super admin cannot be banned'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BanUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user.is_banned = True
            user.ban_reason = serializer.validated_data['reason']
            
            if serializer.validated_data['is_permanent']:
                user.ban_until = None
            else:
                user.ban_until = serializer.validated_data['ban_until']
            
            user.save()
            
            self.send_ban_notification(user)
            
            Notification.objects.create(
                user=user,
                title="Your account has been banned",
                message=f"Your account has been banned. Reason: {user.ban_reason}" + 
                       (f" Until: {user.ban_until.strftime('%Y-%m-%d')}" if user.ban_until else ""),
                link="/support"
            )
            
            return Response({
                'message': 'User has been banned successfully',
                'user': UserSerializer(user).data
            })
        except Exception as e:
            logger.error(f"Failed to ban user: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to ban user'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def send_ban_notification(self, user):
        try:
            subject = "Your account has been banned"
            message = render_to_string('emails/ban_notification.html', {
                'user': user,
                'reason': user.ban_reason,
                'ban_until': user.ban_until.strftime('%Y-%m-%d') if user.ban_until else None,
                'support_url': f"{settings.FRONTEND_BASE_URL}/support.html"
            })
            
            send_mail(
                subject,
                "",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message,
                fail_silently=False
            )
        except Exception as e:
            logger.error(f"Failed to send ban notification email: {str(e)}")

class UnbanUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        if not request.user.is_admin():
            return Response(
                {'message': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = get_object_or_404(User, id=user_id)
        
        if user.is_super_admin() and not request.user.is_super_admin():
            return Response(
                {'message': 'Only super admin can unban other super admins'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            user.is_banned = False
            user.ban_reason = None
            user.ban_until = None
            user.save()
            
            self.send_unban_notification(user)
            
            Notification.objects.create(
                user=user,
                title="Your account has been unbanned",
                message="Your account has been unbanned and you can now access all features.",
                link="/"
            )
            
            return Response({
                'message': 'User has been unbanned successfully',
                'user': UserSerializer(user).data
            })
        except Exception as e:
            logger.error(f"Failed to unban user: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to unban user'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def send_unban_notification(self, user):
        try:
            subject = "Your account has been unbanned"
            message = render_to_string('emails/unban_notification.html', {
                'user': user,
                'login_url': settings.FRONTEND_LOGIN_URL
            })
            
            send_mail(
                subject,
                "",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message,
                fail_silently=False
            )
        except Exception as e:
            logger.error(f"Failed to send unban notification email: {str(e)}")

# ========== Dashboard Views ==========
class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin():
            # Return user-specific stats for regular users
            user_educations = Education.objects.filter(user=request.user).count()
            user_experiences = Experience.objects.filter(user=request.user).count()
            user_documents = UserDocument.objects.filter(user=request.user).count()
            user_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
            
            return Response({
                'user_stats': {
                    'educations': user_educations,
                    'experiences': user_experiences,
                    'documents': user_documents,
                    'notifications': user_notifications,
                    'profile_views': getattr(request.user, 'profile_views', 0)
                },
                'opportunity_stats': {
                    'available': Opportunity.objects.filter(status='approved').count(),
                    'matching': 0,
                    'total_mentors': User.objects.filter(role='mentor').count()
                },
                'profile_completion': {
                    'has_bio': bool(request.user.bio or request.user.short_bio),
                    'has_profile_pic': bool(request.user.profile_pic),
                    'has_education': user_educations > 0,
                    'has_experience': user_experiences > 0,
                    'has_phone': bool(request.user.phone),
                    'has_location': bool(request.user.location)
                }
            })
        
        try:
            total_users = User.objects.count()
            new_users_today = User.objects.filter(date_joined__date=datetime.now().date()).count()
            new_users_this_month = User.objects.filter(
                date_joined__month=datetime.now().month,
                date_joined__year=datetime.now().year
            ).count()
            
            user_growth = User.objects.annotate(
                month=TruncMonth('date_joined')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
            
            role_distribution = User.objects.values('role').annotate(
                count=Count('id')
            ).order_by('-count')
            
            total_mentors = User.objects.filter(role='mentor').count()
            active_mentors = User.objects.filter(
                role='mentor',
                mentor_availability__isnull=False
            ).count()
            
            total_opportunities = Opportunity.objects.count()
            pending_opportunities = Opportunity.objects.filter(status='pending').count()
            
            total_feedbacks = Feedback.objects.count()
            total_reports = Report.objects.count()
            total_cv_reviews = CVReview.objects.count()
            
            recent_notifications = Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')[:5]
            
            recent_users = User.objects.order_by('-date_joined')[:5]
            
            return Response({
                'user_stats': {
                    'total': total_users,
                    'new_today': new_users_today,
                    'new_this_month': new_users_this_month,
                    'growth_by_month': list(user_growth),
                    'role_distribution': list(role_distribution)
                },
                'mentor_stats': {
                    'total': total_mentors,
                    'active': active_mentors
                },
                'opportunity_stats': {
                    'total': total_opportunities,
                    'pending': pending_opportunities
                },
                'engagement_stats': {
                    'feedbacks': total_feedbacks,
                    'reports': total_reports,
                    'cv_reviews': total_cv_reviews
                },
                'recent_activities': {
                    'notifications': NotificationSerializer(recent_notifications, many=True).data,
                    'users': UserSerializer(recent_users, many=True).data
                }
            })
        except Exception as e:
            logger.error(f"Failed to fetch dashboard stats: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch dashboard stats'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CommentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, comment_id):
        try:
            return PostComment.objects.get(id=comment_id)
        except PostComment.DoesNotExist:
            return None
    
    def put(self, request, comment_id):
        comment = self.get_object(comment_id)
        if not comment:
            return Response(
                {'message': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if comment.user != request.user and not request.user.is_admin():
            return Response(
                {'message': 'You can only edit your own comments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PostCommentSerializer(
            comment, 
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            updated_comment = serializer.save()
            return Response(
                PostCommentSerializer(updated_comment).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Failed to update comment: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update comment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, comment_id):
        comment = self.get_object(comment_id)
        if not comment:
            return Response(
                {'message': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if comment.user != request.user and not request.user.is_admin():
            return Response(
                {'message': 'You can only delete your own comments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            comment.delete()
            return Response(
                {'message': 'Comment deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            logger.error(f"Failed to delete comment: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to delete comment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CommentReactionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_comment(self, comment_id):
        try:
            return PostComment.objects.get(id=comment_id)
        except PostComment.DoesNotExist:
            return None
    
    def post(self, request, comment_id):
        comment = self.get_comment(comment_id)
        if not comment:
            return Response(
                {'message': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        reaction_type = request.data.get('reaction_type', 'like')
        
        try:
            # Check if user already reacted to this comment
            existing_reaction = CommentReaction.objects.filter(
                comment=comment,
                user=request.user
            ).first()
            
            if existing_reaction:
                if existing_reaction.reaction_type == reaction_type:
                    # Remove reaction if same type is clicked again
                    existing_reaction.delete()
                    return Response(
                        {'message': 'Reaction removed', 'reaction': None},
                        status=status.HTTP_200_OK
                    )
                else:
                    # Update reaction type
                    existing_reaction.reaction_type = reaction_type
                    existing_reaction.save()
                    return Response(
                        {'message': 'Reaction updated', 'reaction_type': reaction_type},
                        status=status.HTTP_200_OK
                    )
            else:
                # Create new reaction
                CommentReaction.objects.create(
                    comment=comment,
                    user=request.user,
                    reaction_type=reaction_type
                )
                
                # Create notification for comment owner
                if comment.user != request.user:
                    Notification.objects.create(
                        user=comment.user,
                        title=f"Someone liked your comment",
                        message=f"{request.user.full_name} liked your comment",
                        link=f"/user_dashboard/community.html"
                    )
                
                return Response(
                    {'message': 'Reaction added', 'reaction_type': reaction_type},
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            logger.error(f"Failed to process comment reaction: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to process reaction'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ========== Community Discussion Views ==========
class CommunityTopicsView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            from .models import CommunityDiscussion, CommunityReply
            from django.db.models import Count
            
            # Get discussion and reply counts for each topic
            topics_data = {}
            for topic_id, topic_name in CommunityDiscussion.TOPIC_CHOICES:
                discussions = CommunityDiscussion.objects.filter(topic=topic_id)
                discussion_count = discussions.count()
                reply_count = CommunityReply.objects.filter(discussion__topic=topic_id).count()
                total_count = discussion_count + reply_count
                
                topics_data[topic_id] = {
                    'discussions': total_count,
                    'title': topic_name
                }
            
            return Response(topics_data)
        except Exception as e:
            logger.error(f"Error fetching topic stats: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch topic stats'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CommunityDiscussionsView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            from .models import CommunityDiscussion
            from .serializers import CommunityDiscussionSerializer
            
            topic = request.query_params.get('topic')
            discussions = CommunityDiscussion.objects.all()
            
            if topic:
                discussions = discussions.filter(topic=topic)
            
            serializer = CommunityDiscussionSerializer(discussions, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching discussions: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch discussions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        try:
            from .models import CommunityDiscussion
            from .serializers import CommunityDiscussionSerializer
            
            serializer = CommunityDiscussionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            discussion = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating discussion: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create discussion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CommunityDiscussionDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, discussion_id):
        try:
            from .models import CommunityDiscussion
            from .serializers import CommunityDiscussionSerializer
            
            discussion = get_object_or_404(CommunityDiscussion, id=discussion_id)
            serializer = CommunityDiscussionSerializer(discussion)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching discussion: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch discussion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CommunityDiscussionRepliesView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, discussion_id):
        try:
            from .models import CommunityDiscussion, CommunityReply
            from .serializers import CommunityReplySerializer
            
            discussion = get_object_or_404(CommunityDiscussion, id=discussion_id)
            replies = discussion.replies.all()
            serializer = CommunityReplySerializer(replies, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching replies: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch replies'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request, discussion_id):
        try:
            from .models import CommunityDiscussion, CommunityReply
            from .serializers import CommunityReplySerializer
            
            discussion = get_object_or_404(CommunityDiscussion, id=discussion_id)
            serializer = CommunityReplySerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            reply = serializer.save(discussion=discussion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating reply: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create reply'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CommunityReplyDetailView(APIView):
    permission_classes = [AllowAny]
    
    def put(self, request, reply_id):
        try:
            from .models import CommunityReply
            from .serializers import CommunityReplySerializer
            
            reply = get_object_or_404(CommunityReply, id=reply_id)
            serializer = CommunityReplySerializer(reply, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            reply = serializer.save()
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating reply: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update reply'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, reply_id):
        try:
            from .models import CommunityReply
            
            reply = get_object_or_404(CommunityReply, id=reply_id)
            reply.delete()
            return Response({'message': 'Reply deleted successfully'})
        except Exception as e:
            logger.error(f"Error deleting reply: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to delete reply'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PublicOpportunitySubmissionView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Use first admin user as default for public submissions
            default_user = User.objects.filter(role__in=['admin', 'super_admin']).first()
            if not default_user:
                default_user = User.objects.first()
            
            # Create opportunity with public submission metadata
            opportunity = Opportunity.objects.create(
                title=request.data.get('title', ''),
                description=f"[PUBLIC SUBMISSION]\n\nSubmitter: {request.data.get('submitter_name', 'Anonymous')}\nEmail: {request.data.get('submitter_email', 'Not provided')}\n\n{request.data.get('description', '')}",
                opportunity_type=request.data.get('opportunity_type', 'job'),
                deadline_type=request.data.get('deadline_type', 'not_specified'),
                deadline=request.data.get('deadline') if request.data.get('deadline_type') == 'specific' else None,
                organization=request.data.get('organization', ''),
                location=request.data.get('location', ''),
                opportunity_link=request.data.get('opportunity_link', ''),
                featured_image=request.FILES.get('featured_image'),
                organization_logo=request.FILES.get('organization_logo'),
                status='pending',
                created_by=default_user,
                priority_level=-1  # Mark as public submission for admin review
            )
            
            return Response({
                'message': 'Opportunity submitted successfully for review',
                'id': opportunity.id
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Public opportunity submission error: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ServiceRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Validate required fields
            required_fields = ['service_type', 'name', 'email', 'preferred_date']
            for field in required_fields:
                if not request.data.get(field):
                    return Response({
                        'message': f'{field.replace("_", " ").title()} is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            ServiceRequest.objects.create(
                service_type=request.data.get('service_type'),
                name=request.data.get('name'),
                email=request.data.get('email'),
                people_count=int(request.data.get('people_count', 1)),
                preferred_date=request.data.get('preferred_date'),
                link=request.data.get('link', ''),
                file_upload=request.FILES.get('file_upload'),
                description=request.data.get('description', ''),
                additional_info=request.data.get('additional_info', ''),
                contact_info=request.data.get('contact_info', ''),
                status='pending'
            )
            
            return Response({
                'message': 'Service request submitted successfully! We will contact you soon.'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Service request error: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class BlogPostView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            status_filter = request.query_params.get('status', 'published')
            blogs = BlogPost.objects.filter(status=status_filter).order_by('-created_at')
            
            blog_data = []
            for blog in blogs:
                blog_data.append({
                    'id': blog.id,
                    'title': blog.title,
                    'content': blog.content,
                    'excerpt': blog.excerpt,
                    'featured_image': blog.featured_image.url if blog.featured_image else None,
                    'author': blog.author,
                    'author_avatar': blog.author_avatar.url if blog.author_avatar else None,
                    'category': blog.category,
                    'is_featured': blog.is_featured,
                    'read_time': blog.read_time,
                    'created_at': blog.created_at,
                    'published_date': blog.published_date or blog.created_at
                })
            
            return Response({'blogs': blog_data})
        except Exception as e:
            logger.error(f"Error fetching blogs: {str(e)}", exc_info=True)
            return Response({'blogs': []})

class SuccessStorySubmissionView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            from django.utils.html import escape
            import re
            
            # Sanitize inputs
            title = escape(request.data.get('title', '').strip())[:200]
            content = escape(request.data.get('content', '').strip())[:5000]
            author_name = escape(request.data.get('author_name', '').strip())[:100]
            author_email = request.data.get('author_email', '').strip()[:100]
            author_location = escape(request.data.get('author_location', '').strip())[:100]
            
            # Email validation
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', author_email):
                return Response({'message': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)
            
            SuccessStory.objects.create(
                title=title,
                content=content,
                author_name=author_name,
                author_email=author_email,
                author_location=author_location,
                featured_image=request.FILES.get('featured_image'),
                excerpt=content[:150] + '...' if len(content) > 150 else content,
                status='pending'
            )
            
            return Response({
                'message': 'Success story submitted successfully! We will review and publish it soon.'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Success story submission error: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BlogToolkitView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            # Get approved success stories
            success_stories = SuccessStory.objects.filter(status='approved').order_by('-approved_at')
            stories_data = []
            for story in success_stories:
                stories_data.append({
                    'id': story.id,
                    'title': story.title,
                    'excerpt': story.excerpt,
                    'content': story.content,
                    'author_name': story.author_name,
                    'author_location': story.author_location,
                    'featured_image': story.featured_image.url if story.featured_image else None,
                    'approved_at': story.approved_at
                })
            
            # Static tip categories data
            tip_categories = [
                {
                    'name': 'Success Stories',
                    'slug': 'success-stories',
                    'description': 'Inspiring journeys from our community members',
                    'icon': 'fas fa-star',
                    'tips': []
                },
                {
                    'name': 'CV & Resume Tips',
                    'slug': 'cv-resume-tips',
                    'description': 'Expert advice for crafting compelling resumes',
                    'icon': 'fas fa-file-alt',
                    'tips': []
                },
                {
                    'name': 'Cover Letter Help',
                    'slug': 'cover-letter-help',
                    'description': 'Write cover letters that get noticed',
                    'icon': 'fas fa-envelope',
                    'tips': []
                },
                {
                    'name': 'Internship Tips',
                    'slug': 'internship-tips',
                    'description': 'Land your dream internship opportunity',
                    'icon': 'fas fa-briefcase',
                    'tips': []
                },
                {
                    'name': 'Mentorship Insights',
                    'slug': 'mentorship-insights',
                    'description': 'Make the most of mentorship relationships',
                    'icon': 'fas fa-user-tie',
                    'tips': []
                },
                {
                    'name': 'Landing Opportunities',
                    'slug': 'landing-opportunities',
                    'description': 'Strategies for securing great opportunities',
                    'icon': 'fas fa-rocket',
                    'tips': []
                }
            ]
            
            # Get tip categories with tips and files from database
            from .models import TipCategory
            tip_categories = TipCategory.objects.filter(is_active=True).order_by('order')
            categories_data = []
            for category in tip_categories:
                tips_data = []
                for tip in category.tips.filter(is_active=True).order_by('order'):
                    tips_data.append({
                        'id': tip.id,
                        'title': tip.title,
                        'explanation': tip.explanation
                    })
                
                files_data = []
                for file in category.files.filter(is_active=True):
                    files_data.append({
                        'id': file.id,
                        'title': file.title,
                        'file_url': file.file.url if file.file else None,
                        'description': file.description
                    })
                
                categories_data.append({
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'description': category.description,
                    'icon': category.icon,
                    'tips': tips_data,
                    'files': files_data
                })
            
            # Get team members
            from .models import TeamMember, Partner
            team_members = TeamMember.objects.filter(is_active=True).order_by('order')
            team_data = []
            for member in team_members:
                team_data.append({
                    'id': member.id,
                    'name': member.name,
                    'position': member.position,
                    'description': member.description,
                    'image': member.image.url if member.image else None,
                    'linkedin_url': member.linkedin_url,
                    'facebook_url': member.facebook_url,
                    'instagram_url': member.instagram_url,
                    'twitter_url': member.twitter_url,
                    'email': member.email
                })
            
            # Get partners
            partners = Partner.objects.filter(is_active=True).order_by('order')
            partners_data = []
            for partner in partners:
                partners_data.append({
                    'id': partner.id,
                    'name': partner.name,
                    'description': partner.description,
                    'logo': partner.logo.url if partner.logo else None,
                    'website_url': partner.website_url,
                    'partnership_type': partner.partnership_type
                })
            
            # Get about sections with defaults
            from .models import AboutSection, HeroSlide
            about_sections = AboutSection.objects.filter(is_active=True)
            sections_data = {}
            
            # Default content for sections
            default_sections = {
                'who_we_are': {
                    'title': 'WHO WE ARE',
                    'subtitle': 'Learn Who we are',
                    'content': 'We are a dynamic and passionate team of mentors, educators, and professionals dedicated to empowering the next generation. Youth Opportunities was founded with the vision to bridge the gap between young people and the resources they need to succeed. Our team is united by a shared mission: to provide youth with the tools, guidance, and opportunities they need to confidently step into their futures.\n\nAt the heart of our organization are individuals who deeply care about the development of youth. Our team consists of experienced mentors who are committed to nurturing talent, educators who create insightful and relevant content, and professionals who bring a wealth of industry experience to the table. Together, we work to ensure that every young person has access to meaningful resources and personalized support.\n\nWe believe in the power of mentorship, community, and self-discovery. With a focus on creating inclusive and diverse pathways for growth, we strive to inspire and guide young individuals, helping them realize their full potential and encouraging them to dream big.'
                },
                'our_mission': {
                    'title': 'OUR MISSION',
                    'subtitle': 'Our Mission',
                    'content': 'At Youth Opportunities, our mission is to empower young individuals by providing them with access to essential career resources, mentorship, and growth opportunities. We are committed to connecting youth with the tools and guidance they need to navigate their educational and professional journeys with confidence.\n\nThrough personalized mentorship, career development programs, and exclusive opportunities, we aim to foster a community of young people who are equipped to succeed in today\'s fast-changing world. Our goal is to inspire youth to discover their potential, embrace their talents, and confidently pursue their dreams, while building a supportive network that encourages lifelong learning and success.'
                },
                'our_vision': {
                    'title': 'OUR VISION',
                    'subtitle': 'Our Vision',
                    'content': 'At Youth Opportunities, our vision is to create a world where every young person has access to the resources, mentorship, and opportunities they need to thrive. We envision a future where geographical boundaries, economic limitations, and social barriers do not prevent talented youth from achieving their dreams.\n\nWe strive to build a global community that celebrates diversity, fosters innovation, and empowers the next generation of leaders, entrepreneurs, and change-makers. Our vision is to be the bridge that connects young talent with life-changing opportunities, creating a ripple effect of positive impact across communities worldwide.'
                },
                'founded_in': {
                    'title': 'FOUNDED IN',
                    'subtitle': 'When was it founded?',
                    'content': 'Youth Opportunities Uniting Talent and Hope was founded in 2024 with a clear vision to create a platform that would serve as a bridge between young talents and life-changing opportunities. Born from the recognition that many young people struggle to find and access quality opportunities due to information gaps and limited networks, our platform was created to democratize access to internships, scholarships, fellowships, jobs, and other growth opportunities.\n\nSince our founding, we have grown from a simple idea into a comprehensive platform that serves thousands of young people worldwide, connecting them with opportunities that inspire growth, exposure, and hope for a brighter future.'
                },
                'what_we_offer': {
                    'title': 'WHAT WE OFFER',
                    'subtitle': 'Learn about what we offer',
                    'content': 'At Youth Opportunities, we offer a comprehensive suite of resources and services designed to empower young people in their career and personal development journey:\n\n• Opportunity Sharing: Access to thousands of internships, scholarships, fellowships, jobs, conferences, workshops, and training programs from around the world.\n• Career Guidance: Expert tips on resume writing, cover letter crafting, interview preparation, and professional development.\n• Mentorship Programs: Connect with experienced professionals who provide personalized guidance and support.\n• Community Platform: Engage with like-minded peers, share experiences, and build valuable networks.\n• Success Stories: Learn from others who have successfully navigated their career journeys.\n• Educational Resources: Access to blogs, articles, and educational content that enhance your knowledge and skills.'
                },
                'our_impact': {
                    'title': 'OUR IMPACT',
                    'subtitle': 'Learn about our impacts',
                    'content': 'Since our founding in 2024, Youth Opportunities has made a significant impact in the lives of young people worldwide:\n\n• Thousands of Opportunities Shared: We have curated and shared thousands of verified opportunities, helping young people discover paths they never knew existed.\n• Global Reach: Our platform serves young people from diverse backgrounds across multiple continents, breaking down geographical barriers to opportunity access.\n• Success Stories: Hundreds of young people have successfully secured internships, scholarships, and jobs through our platform, with many sharing their inspiring journeys.\n• Community Building: We have fostered a supportive community where young people can connect, learn from each other, and build lasting professional relationships.\n• Career Development: Through our resources and guidance, we have helped countless individuals improve their job readiness skills and professional confidence.'
                }
            }
            
            # Use database content if available, otherwise use defaults
            for section in about_sections:
                sections_data[section.section_type] = {
                    'title': section.title,
                    'subtitle': section.subtitle,
                    'content': section.content,
                    'image': section.image.url if section.image else None
                }
            
            # Fill in missing sections with defaults
            for key, default in default_sections.items():
                if key not in sections_data:
                    sections_data[key] = default
            
            # Get hero slides
            hero_slides = HeroSlide.objects.filter(is_active=True).order_by('order')
            slides_data = []
            for slide in hero_slides:
                slides_data.append({
                    'title': slide.title,
                    'subtitle': slide.subtitle,
                    'description': slide.description,
                    'image': slide.image.url if slide.image else None
                })
            
            return Response({
                'success_stories': stories_data,
                'tip_categories': categories_data,
                'team_members': team_data,
                'partners': partners_data,
                'about_sections': sections_data,
                'hero_slides': slides_data
            })
        except Exception as e:
            logger.error(f"Error fetching blog toolkit: {str(e)}", exc_info=True)
            return Response({'success_stories': [], 'tip_categories': []})

class NewsletterSubscribeView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email')
            name = request.data.get('name', '')
            
            if not email:
                return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create or get newsletter subscriber
            from .models import NewsletterSubscriber
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'is_active': True
                }
            )
            
            if created:
                message = 'Successfully subscribed to newsletter!'
            else:
                message = 'You are already subscribed to our newsletter!'
            
            return Response({'message': message})
        except Exception as e:
            logger.error(f"Newsletter subscription error: {str(e)}", exc_info=True)
            return Response({'message': 'Failed to subscribe. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MentorApplicationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            applications = MentorApplication.objects.filter(user=request.user)
            serializer = MentorApplicationSerializer(applications, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch mentor applications: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch mentor applications'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        try:
            if request.user.role == 'mentor':
                return Response(
                    {'message': 'You are already a mentor'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user already has a pending application
            existing_app = MentorApplication.objects.filter(
                user=request.user,
                status__in=['submitted', 'in_review', 'interview']
            ).first()
            
            if existing_app:
                return Response(
                    {'message': 'You cannot submit another application until a decision is made on your current application'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            application = MentorApplication.objects.create(
                user=request.user,
                years_experience=int(request.data.get('years_experience', 0)),
                why_mentor=request.data.get('why_mentor', ''),
                agree_to_terms=request.data.get('agree_to_terms', False),
                agree_to_volunteer=request.data.get('agree_to_volunteer', False),
                status='submitted'
            )
            
            return Response({
                'message': 'Mentor application submitted successfully',
                'application': MentorApplicationSerializer(application).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to submit mentor application: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to submit mentor application'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InternalDiscussionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            topic = request.query_params.get('topic')
            discussions = InternalDiscussion.objects.all()
            
            if topic:
                discussions = discussions.filter(topic=topic)
            
            serializer = InternalDiscussionSerializer(discussions, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch internal discussions: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch discussions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        try:
            serializer = InternalDiscussionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            discussion = serializer.save(user=request.user)
            return Response(
                InternalDiscussionSerializer(discussion).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Failed to create internal discussion: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create discussion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InternalDiscussionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, discussion_id):
        try:
            discussion = get_object_or_404(InternalDiscussion, id=discussion_id, user=request.user)
            serializer = InternalDiscussionSerializer(discussion, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            updated_discussion = serializer.save()
            return Response(InternalDiscussionSerializer(updated_discussion).data)
        except Exception as e:
            logger.error(f"Failed to update discussion: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update discussion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, discussion_id):
        try:
            discussion = get_object_or_404(InternalDiscussion, id=discussion_id, user=request.user)
            discussion.delete()
            return Response({'message': 'Discussion deleted successfully'})
        except Exception as e:
            logger.error(f"Failed to delete discussion: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to delete discussion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InternalDiscussionReplyDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, reply_id):
        try:
            reply = get_object_or_404(InternalDiscussionReply, id=reply_id, user=request.user)
            serializer = InternalDiscussionReplySerializer(reply, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            updated_reply = serializer.save()
            return Response(InternalDiscussionReplySerializer(updated_reply).data)
        except Exception as e:
            logger.error(f"Failed to update reply: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to update reply'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, reply_id):
        try:
            reply = get_object_or_404(InternalDiscussionReply, id=reply_id, user=request.user)
            reply.delete()
            return Response({'message': 'Reply deleted successfully'})
        except Exception as e:
            logger.error(f"Failed to delete reply: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to delete reply'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InternalDiscussionRepliesView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, discussion_id):
        try:
            discussion = get_object_or_404(InternalDiscussion, id=discussion_id)
            replies = discussion.replies.all()
            serializer = InternalDiscussionReplySerializer(replies, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to fetch discussion replies: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to fetch replies'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request, discussion_id):
        try:
            discussion = get_object_or_404(InternalDiscussion, id=discussion_id)
            serializer = InternalDiscussionReplySerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            reply = serializer.save(user=request.user, discussion=discussion)
            return Response(
                InternalDiscussionReplySerializer(reply).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Failed to create discussion reply: {str(e)}", exc_info=True)
            return Response(
                {'message': 'Failed to create reply'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@csrf_exempt
def faq_view(request):
    if request.method == 'GET':
        try:
            from .models import FAQ
            faqs = FAQ.objects.filter(is_active=True).order_by('order')
            faq_data = []
            
            for faq in faqs:
                faq_data.append({
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer,
                    'order': faq.order
                })
            
            return JsonResponse({
                'status': 'success',
                'faqs': faq_data
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

