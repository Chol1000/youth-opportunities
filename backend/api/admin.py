from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    User, Education, Experience, UserDocument,
    Opportunity, Notification, MentorRequest, MentorshipSession,
    Feedback, Advertisement, CollaborationRequest, TrainingSession,
    TrainingRegistration,
    Report, CVReview, ApplicationGuidance,
    InterviewPreparation, ProfileOptimization, SuccessTip, Webinar,
    WebinarRegistration, CommunityPost, PostComment, PostReaction,
    CommunityDiscussion, CommunityReply, ServiceRequest, BlogPost, SuccessStory,
    TipCategory, Tip, TipFile, NewsletterSubscriber, TeamMember, Partner,
    AboutSection, HeroSlide, FAQ, MentorApplication, InternalDiscussion, InternalDiscussionReply,
    ChatRoom, ChatMessage
)

# Inline classes for User admin
class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
    fields = ['institution', 'degree', 'level', 'field_of_study', 'start_date', 'end_date', 'is_current', 'grade']
    readonly_fields = ['created_at', 'updated_at']
    classes = ['collapse']

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0
    fields = ['company', 'title', 'location', 'start_date', 'end_date', 'currently_working']
    readonly_fields = ['created_at', 'updated_at']
    classes = ['collapse']

class UserDocumentInline(admin.TabularInline):
    model = UserDocument
    extra = 0
    fields = ['title', 'document_type', 'file', 'uploaded_at']
    readonly_fields = ['uploaded_at', 'updated_at']
    classes = ['collapse']

class MentorRequestInline(admin.TabularInline):
    model = MentorRequest
    fk_name = 'mentee'
    extra = 0
    fields = ['mentor', 'topic', 'status', 'created_at']
    readonly_fields = ['created_at']
    classes = ['collapse']

class CVReviewInline(admin.TabularInline):
    model = CVReview
    fk_name = 'user'
    extra = 0
    fields = ['cv_file', 'status', 'submitted_at']
    readonly_fields = ['submitted_at']
    classes = ['collapse']

class NotificationInline(admin.TabularInline):
    model = Notification
    extra = 0
    fields = ['title', 'message', 'is_read', 'created_at']
    readonly_fields = ['created_at']
    max_num = 5  # Limit to show only recent 5 notifications
    classes = ['collapse']

# Main User Admin with inlines
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']
    list_editable = ['role', 'is_active']
    
    inlines = [EducationInline, ExperienceInline, UserDocumentInline, MentorRequestInline, CVReviewInline, NotificationInline]
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('email', 'first_name', 'last_name', 'profile_pic')
        }),
        ('Contact Info', {
            'fields': ('phone', 'location')
        }),
        ('Bio & Preferences', {
            'fields': ('bio', 'short_bio', 'expertise', 'preferences')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Ban Information', {
            'fields': ('is_banned', 'ban_reason', 'ban_until'),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

# Opportunity Management
@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'opportunity_type', 'status', 'created_by', 'deadline', 'created_at']
    list_filter = ['opportunity_type', 'status', 'created_at', 'deadline']
    search_fields = ['title', 'description', 'organization']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set defaults for new objects
            obj.created_by = request.user
            # Notify all users about new webinar
            from .models import Notification
            from django.contrib.auth import get_user_model
            User = get_user_model()
            users = User.objects.filter(is_active=True).exclude(id=request.user.id)
            for user in users:
                Notification.objects.create(
                    user=user,
                    title="New Webinar Available",
                    message=f"A new webinar '{obj.title}' has been scheduled.",
                    link="/user_dashboard/webinars.html"
                )
            # Set default values for fields that might not have defaults in DB
            if not hasattr(obj, 'views_count') or obj.views_count is None:
                obj.views_count = 0
            if not hasattr(obj, 'clicks_count') or obj.clicks_count is None:
                obj.clicks_count = 0
            if not hasattr(obj, 'shares_count') or obj.shares_count is None:
                obj.shares_count = 0
        super().save_model(request, obj, form, change)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'opportunity_type', 'subtype')
        }),
        ('Details', {
            'fields': ('organization', 'organization_logo', 'location', 'deadline', 'deadline_type', 'application_link')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Status', {
            'fields': ('status', 'is_featured', 'priority_level')
        }),
        ('Metadata', {
            'fields': ('tags', 'additional_filters', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Service Requests (MentorRequest)
@admin.register(MentorRequest)
class MentorRequestAdmin(admin.ModelAdmin):
    list_display = ['mentee', 'mentor', 'topic', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['mentee__email', 'mentor__email', 'topic']
    list_editable = ['status']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('mentee', 'mentor', 'topic', 'message')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__email', 'title', 'message']
    list_editable = ['is_read']

@admin.register(MentorshipSession)
class MentorshipSessionAdmin(admin.ModelAdmin):
    list_display = ['mentor', 'mentee', 'scheduled_time', 'duration', 'is_completed']
    list_filter = ['is_completed', 'scheduled_time']
    search_fields = ['mentor__email', 'mentee__email']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['user__email', 'subject', 'message']

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'start_date', 'end_date', 'created_by']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'content']

@admin.register(CollaborationRequest)
class CollaborationRequestAdmin(admin.ModelAdmin):
    list_display = ['organization_name', 'requester', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['organization_name', 'requester__email']

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'trainer', 'start_time', 'duration', 'max_participants', 'is_active']
    list_filter = ['is_active', 'start_time', 'trainer']
    search_fields = ['title', 'description', 'trainer__email', 'trainer__first_name', 'trainer__last_name']
    list_editable = ['is_active']
    readonly_fields = ['created_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new training sessions
            # Notify all users about new training
            from .models import Notification
            from django.contrib.auth import get_user_model
            User = get_user_model()
            users = User.objects.filter(is_active=True).exclude(id=request.user.id)
            for user in users:
                Notification.objects.create(
                    user=user,
                    title="New Training Session Available",
                    message=f"A new training session '{obj.title}' has been added.",
                    link="/user_dashboard/training.html"
                )
        super().save_model(request, obj, form, change)
    class TrainingRegistrationInline(admin.TabularInline):
        model = TrainingRegistration
        extra = 0
        fields = ['user', 'registered_at', 'attended']
        readonly_fields = ['registered_at']
    
    inlines = [TrainingRegistrationInline]
    
    fieldsets = (
        ('Training Information', {
            'fields': ('title', 'description', 'trainer')
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time', 'duration', 'max_participants', 'meeting_link')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

class TrainingRegistrationInline(admin.TabularInline):
    model = TrainingRegistration
    extra = 0
    fields = ['user', 'registered_at', 'attended']
    readonly_fields = ['registered_at']
    


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'report_type', 'subject', 'status', 'created_at']
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['reporter__email', 'subject']

@admin.register(ApplicationGuidance)
class ApplicationGuidanceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content']

@admin.register(InterviewPreparation)
class InterviewPreparationAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'content']

@admin.register(ProfileOptimization)
class ProfileOptimizationAdmin(admin.ModelAdmin):
    list_display = ['title', 'platform', 'created_at']
    list_filter = ['platform', 'created_at']
    search_fields = ['title', 'content']

@admin.register(SuccessTip)
class SuccessTipAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content']

class WebinarRegistrationInline(admin.TabularInline):
    model = WebinarRegistration
    extra = 0
    readonly_fields = ['registered_at']
    fields = ['user', 'attended', 'registered_at']

@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    list_display = ['title', 'presenter', 'start_time', 'is_active']
    list_filter = ['is_active', 'start_time']
    search_fields = ['title', 'presenter__email']
    inlines = [WebinarRegistrationInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new webinars
            # Notify all users about new webinar
            from .models import Notification
            from django.contrib.auth import get_user_model
            User = get_user_model()
            users = User.objects.filter(is_active=True).exclude(id=request.user.id)
            for user in users:
                Notification.objects.create(
                    user=user,
                    title="New Webinar Available",
                    message=f"A new webinar '{obj.title}' has been scheduled.",
                    link="/user_dashboard/webinars.html"
                )
        super().save_model(request, obj, form, change)



class PostCommentInline(admin.TabularInline):
    model = PostComment
    extra = 0
    fields = ['user', 'content', 'created_at']
    readonly_fields = ['created_at']

class PostReactionInline(admin.TabularInline):
    model = PostReaction
    extra = 0
    fields = ['user', 'created_at']
    readonly_fields = ['created_at']

@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'content']
    inlines = [PostCommentInline, PostReactionInline]
    
    def content_preview(self, obj):
        if obj.content:
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return 'No content'
    content_preview.short_description = 'Content'





# Register UserDocument as standalone model (Education and Experience are managed through User admin)
@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'document_type', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['user__email', 'title']

@admin.register(CVReview)
class CVReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'score', 'submitted_at', 'reviewed_by']
    list_filter = ['status', 'submitted_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['submitted_at', 'created_at', 'updated_at']
    list_editable = ['status']
    
    fieldsets = (
        ('CV Information', {
            'fields': ('user', 'cv_file', 'additional_info')
        }),
        ('Review Status', {
            'fields': ('status', 'feedback', 'score', 'reviewed_by')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'reviewed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and obj.status == 'completed' and not obj.reviewed_at:
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)

class CommunityReplyInline(admin.TabularInline):
    model = CommunityReply
    extra = 0
    fields = ['content', 'is_anonymous', 'created_at']
    readonly_fields = ['created_at']

@admin.register(CommunityDiscussion)
class CommunityDiscussionAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'is_anonymous', 'created_at']
    list_filter = ['topic', 'is_anonymous', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']
    inlines = [CommunityReplyInline]
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'email', 'status', 'preferred_date', 'created_at']
    list_filter = ['service_type', 'status', 'created_at']
    search_fields = ['name', 'email', 'description']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')

# Admin site customization
admin.site.site_header = "Youth Opportunities Admin"
admin.site.site_title = "Youth Opportunities Admin Portal"
admin.site.index_title = "Welcome to Youth Opportunities Administration"
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'category', 'is_featured', 'created_at']
    search_fields = ['title', 'content', 'author']
    readonly_fields = ['created_at']
    list_editable = ['status', 'is_featured']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')

@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author_name', 'author_email', 'status']
    list_filter = ['status']
    search_fields = ['title', 'author_name', 'author_email', 'content']
    list_editable = ['status']
    
    def save_model(self, request, obj, form, change):
        if obj.status == 'approved' and not obj.approved_at:
            obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)

class TipInline(admin.TabularInline):
    model = Tip
    extra = 0
    fields = ['title', 'explanation', 'order', 'is_active']
    ordering = ['order']

class TipFileInline(admin.TabularInline):
    model = TipFile
    extra = 0
    fields = ['title', 'file', 'description', 'is_active']

@admin.register(TipCategory)
class TipCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    inlines = [TipInline, TipFileInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'icon')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )

# Remove standalone registrations - Tips and TipFiles are now only managed through TipCategory
# @admin.register(Tip) - Commented out
# @admin.register(TipFile) - Commented out

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at']
    list_editable = ['is_active']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-subscribed_at')

class TeamMemberInline(admin.StackedInline):
    model = TeamMember
    extra = 0
    fields = ['name', 'position', 'description', 'image', 'linkedin_url', 'facebook_url', 'instagram_url', 'twitter_url', 'email', 'order', 'is_active']

class PartnerInline(admin.StackedInline):
    model = Partner
    extra = 0
    fields = ['name', 'description', 'logo', 'website_url', 'partnership_type', 'order', 'is_active']

class HeroSlideInline(admin.StackedInline):
    model = HeroSlide
    extra = 0
    fields = ['title', 'subtitle', 'description', 'image', 'order', 'is_active']

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['section_type', 'title', 'is_active', 'updated_at']
    list_filter = ['section_type', 'is_active']
    search_fields = ['title', 'content']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Section Information', {
            'fields': ('section_type', 'title', 'subtitle', 'content', 'image')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )
    
    # Removed inlines - using standalone admin sections instead

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('FAQ Content', {
            'fields': ('question', 'answer')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'position']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'position', 'description', 'image')
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'facebook_url', 'instagram_url', 'twitter_url', 'email')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'partnership_type', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'partnership_type', 'created_at']
    search_fields = ['name', 'partnership_type']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'logo', 'partnership_type')
        }),
        ('Contact', {
            'fields': ('website_url',)
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'description']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('Slide Content', {
            'fields': ('title', 'subtitle', 'description', 'image')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )

class InternalDiscussionReplyInline(admin.TabularInline):
    model = InternalDiscussionReply
    extra = 0
    fields = ['user', 'content', 'created_at']
    readonly_fields = ['created_at']

@admin.register(InternalDiscussion)
class InternalDiscussionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'topic', 'created_at']
    list_filter = ['topic', 'created_at']
    search_fields = ['title', 'content', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [InternalDiscussionReplyInline]
    
    fieldsets = (
        ('Discussion Information', {
            'fields': ('user', 'title', 'content', 'topic')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MentorApplication)
class MentorApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'years_experience', 'status', 'created_at']
    list_filter = ['status', 'years_experience', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Applicant Information', {
            'fields': ('user', 'years_experience')
        }),
        ('Application Content', {
            'fields': ('why_mentor', 'agree_to_terms', 'agree_to_volunteer')
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ChatRoom and ChatMessage are intentionally not registered in admin for privacy
# Messages are encrypted and should not be accessible to administrators
