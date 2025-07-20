from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import (
    User, Education, Experience, UserDocument,
    Opportunity, Notification, MentorRequest, MentorshipSession,
    Feedback, Advertisement, CollaborationRequest, TrainingSession,
    TrainingRegistration,
    Report, CVReview, ApplicationGuidance,
    InterviewPreparation, ProfileOptimization, SuccessTip, Webinar,
    WebinarRegistration, CommunityPost, PostComment, PostReaction,
    CommunityDiscussion, CommunityReply, MentorApplication, InternalDiscussion, InternalDiscussionReply
)

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role', 
                 'profile_pic', 'phone', 'location', 'bio', 'short_bio', 'expertise', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirm_password']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'location', 'bio', 'short_bio', 'profile_pic', 'expertise']

class EducationSerializer(serializers.ModelSerializer):
    level = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Education
        fields = ['id', 'institution', 'degree', 'field_of_study', 'level', 'start_date', 'end_date', 'description']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        validated_data.pop('level', None)  # Remove level if present
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data.pop('level', None)  # Remove level if present
        return super().update(instance, validated_data)

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'company', 'title', 'location', 'start_date', 'end_date', 'currently_working', 'description', 'skills']
        read_only_fields = ['id']

class UserDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocument
        fields = '__all__'
        read_only_fields = ['user', 'uploaded_at', 'updated_at']

class OpportunitySerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    featured_image = serializers.SerializerMethodField()
    organization_logo = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Opportunity
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'views_count', 'clicks_count', 'shares_count']
    
    def create(self, validated_data):
        # Handle files and URL fields from request
        request = self.context.get('request')
        if request:
            if request.FILES:
                if 'organization_logo' in request.FILES:
                    validated_data['organization_logo'] = request.FILES['organization_logo']
                if 'featured_image' in request.FILES:
                    validated_data['featured_image'] = request.FILES['featured_image']
            
            # Handle application link
            if 'opportunity_link' in request.data:
                validated_data['application_link'] = request.data['opportunity_link']
        
        return super().create(validated_data)
    
    def validate(self, data):
        # Make deadline_type optional with default
        if 'deadline_type' not in data:
            data['deadline_type'] = 'specific' if data.get('deadline') else 'not_specified'
        return data
    
    def get_featured_image(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None
    
    def get_organization_logo(self, obj):
        if obj.organization_logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.organization_logo.url)
            return obj.organization_logo.url
        return None
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at']

class MentorRequestSerializer(serializers.ModelSerializer):
    mentor = UserSerializer(read_only=True)
    mentee = UserSerializer(read_only=True)
    
    class Meta:
        model = MentorRequest
        fields = '__all__'
        read_only_fields = ['mentee', 'mentor', 'created_at', 'updated_at']

class MentorshipSessionSerializer(serializers.ModelSerializer):
    mentor = UserSerializer(read_only=True)
    mentee = UserSerializer(read_only=True)
    
    class Meta:
        model = MentorshipSession
        fields = '__all__'
        read_only_fields = ['created_at']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']

class CollaborationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaborationRequest
        fields = '__all__'
        read_only_fields = ['requester', 'created_at']


        read_only_fields = ['created_at']



class TrainingSessionSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source='trainer.full_name', read_only=True)
    
    class Meta:
        model = TrainingSession
        fields = '__all__'
        read_only_fields = ['created_at']

class TrainingRegistrationSerializer(serializers.ModelSerializer):
    session = TrainingSessionSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = TrainingRegistration
        fields = '__all__'
        read_only_fields = ['registered_at', 'completed_at']



class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['reporter', 'created_at']

class CVReviewSerializer(serializers.ModelSerializer):
    reviewed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CVReview
        fields = '__all__'
        read_only_fields = ['user', 'submitted_at', 'reviewed_at', 'created_at', 'updated_at']
    
    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.full_name
        return None

class ApplicationGuidanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationGuidance
        fields = '__all__'
        read_only_fields = ['created_at']

class InterviewPreparationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewPreparation
        fields = '__all__'
        read_only_fields = ['created_at']

class ProfileOptimizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileOptimization
        fields = '__all__'
        read_only_fields = ['created_at']

class SuccessTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuccessTip
        fields = '__all__'
        read_only_fields = ['created_at']

class WebinarSerializer(serializers.ModelSerializer):
    presenter = UserSerializer(read_only=True)
    
    class Meta:
        model = Webinar
        fields = ['id', 'title', 'description', 'presenter', 'start_time', 'end_time', 'meeting_link', 'is_active', 'created_at']
        read_only_fields = ['created_at']

class WebinarRegistrationSerializer(serializers.ModelSerializer):
    webinar = WebinarSerializer(read_only=True)
    
    class Meta:
        model = WebinarRegistration
        fields = '__all__'
        read_only_fields = ['registered_at']

class UserRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

class BanUserSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500)
    is_permanent = serializers.BooleanField(default=False)
    ban_until = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate(self, attrs):
        if not attrs.get('is_permanent') and not attrs.get('ban_until'):
            raise serializers.ValidationError("ban_until is required for temporary bans")
        return attrs

class CommunityPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    share_count = serializers.SerializerMethodField()
    has_reacted = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    shared_post = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()
    
    class Meta:
        model = CommunityPost
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_like_count(self, obj):
        return obj.reactions.count()
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_share_count(self, obj):
        return 0  # Simplified - no sharing
    
    def get_has_reacted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.reactions.filter(user=request.user).exists()
        return False
    
    def get_comments(self, obj):
        comments = obj.comments.filter(parent_comment__isnull=True).order_by('created_at')
        return PostCommentSerializer(comments, many=True, context=self.context).data
    
    def get_shared_post(self, obj):
        return None  # Simplified - no sharing
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_video(self, obj):
        return None  # Simplified - no video
    
    def get_document(self, obj):
        return None  # Simplified - no documents

class CommunityPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityPost
        fields = ['content', 'image']

class PostCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()
    has_reacted = serializers.SerializerMethodField()
    
    class Meta:
        model = PostComment
        fields = '__all__'
        read_only_fields = ['user', 'post', 'created_at', 'updated_at']
    
    def get_replies_count(self, obj):
        return 0  # Simplified - no replies
    
    def get_reactions_count(self, obj):
        return 0  # Simplified - no reactions
    
    def get_has_reacted(self, obj):
        return False  # Simplified - no reactions



class CommunityDiscussionSerializer(serializers.ModelSerializer):
    replies_count = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = CommunityDiscussion
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_replies_count(self, obj):
        return obj.replies.count()
    
    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommunityReplySerializer(replies, many=True).data

class CommunityReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityReply
        fields = '__all__'
        read_only_fields = ['discussion', 'created_at']

class MentorApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorApplication
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

class InternalDiscussionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = InternalDiscussion
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_replies_count(self, obj):
        return obj.replies.count()

class InternalDiscussionReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = InternalDiscussionReply
        fields = '__all__'
        read_only_fields = ['user', 'discussion', 'created_at', 'updated_at']

class PostReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PostReaction
        fields = '__all__'
        read_only_fields = ['user', 'post', 'created_at']
