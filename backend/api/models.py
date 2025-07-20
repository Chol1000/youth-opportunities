from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.core.validators import FileExtensionValidator
import os

def opportunity_image_path(instance, filename):
    return f'opportunities/{instance.id}/{filename}'

def user_profile_pic_path(instance, filename):
    return f'profile_pics/{instance.id}/{filename}'



def community_post_image_path(instance, filename):
    return f'community_posts/images/{instance.id}/{filename}'

def cv_file_path(instance, filename):
    return f'cv_files/{instance.id}/{filename}'

def user_document_path(instance, filename):
    return f'user_documents/{instance.id}/{filename}'

def advertisement_image_path(instance, filename):
    return f'advertisements/{instance.id}/{filename}'

def training_materials_path(instance, filename):
    return f'training_materials/{instance.id}/{filename}'

def webinar_materials_path(instance, filename):
    return f'webinar_materials/{instance.id}/{filename}'

def report_attachment_path(instance, filename):
    return f'report_attachments/{instance.id}/{filename}'

def feedback_attachment_path(instance, filename):
    return f'feedback_attachments/{instance.id}/{filename}'





class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    ]
    
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    profile_pic = models.ImageField(upload_to=user_profile_pic_path, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    short_bio = models.CharField(max_length=160, blank=True, default='')
    expertise = models.TextField(blank=True, default='')
    preferences = models.JSONField(default=dict, blank=True)
    is_verified = models.BooleanField(default=False)
    profile_views = models.PositiveIntegerField(default=0)
    mentor_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True, null=True)
    ban_until = models.DateTimeField(blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self):
        return self.role in ['admin', 'super_admin']
    
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    @property
    def is_banned_now(self):
        if not self.is_banned:
            return False
        if self.ban_until and self.ban_until < timezone.now():
            self.is_banned = False
            self.ban_reason = None
            self.ban_until = None
            self.save()
            return False
        return True

class Opportunity(models.Model):
    OPPORTUNITY_TYPES = [
        ('scholarship', 'Scholarship'),
        ('job', 'Job'),
        ('internship', 'Internship'),
        ('fellowship', 'Fellowship'),
        ('grant', 'Grant'),
        ('competition', 'Competition'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('training', 'Training'),
        ('service', 'Service'),
        ('blog', 'Blog'),
        ('announcement', 'Announcement'),
        ('miscellaneous', 'Miscellaneous'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    DEADLINE_TYPES = [
        ('specific', 'Specific'),
        ('rolling', 'Rolling'),
        ('ongoing', 'Ongoing'),
        ('not_specified', 'Not Specified'),
    ]
    
    title = models.CharField(max_length=200)
    description = RichTextField()
    opportunity_type = models.CharField(max_length=20, choices=OPPORTUNITY_TYPES)
    subtype = models.CharField(max_length=100, blank=True, default='')
    organization = models.CharField(max_length=200, default='')
    organization_logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, default='')
    deadline = models.DateTimeField(blank=True, null=True)
    deadline_type = models.CharField(max_length=20, choices=DEADLINE_TYPES, default='specific')
    application_link = models.URLField(blank=True, default='')
    opportunity_link = models.URLField(blank=True, default='')
    requirements = RichTextField(blank=True)
    eligibility_criteria = RichTextField(blank=True)
    benefits = RichTextField(blank=True)
    image = models.ImageField(upload_to=opportunity_image_path, blank=True, null=True)
    featured_image = models.ImageField(upload_to='opportunity_featured/', blank=True, null=True)
    additional_images = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    additional_filters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    priority_level = models.IntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    clicks_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_opportunities')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email}: {self.title}"

class Education(models.Model):
    EDUCATION_LEVELS = [
        ('high_school', 'High School'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    level = models.CharField(max_length=20, choices=EDUCATION_LEVELS)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    grade = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"

class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    currently_working = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.title} at {self.company}"

class UserDocument(models.Model):
    DOCUMENT_TYPES = [
        ('cv', 'CV/Resume'),
        ('cover_letter', 'Cover Letter'),
        ('transcript', 'Academic Transcript'),
        ('certificate', 'Certificate'),
        ('portfolio', 'Portfolio'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=user_document_path)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"

class MentorRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_requests')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorship_requests')
    topic = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.mentee.email} -> {self.mentor.email}: {self.topic}"

class MentorshipSession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_sessions')
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentee_sessions')
    request = models.ForeignKey(MentorRequest, on_delete=models.CASCADE, null=True, blank=True)
    scheduled_time = models.DateTimeField()
    duration = models.PositiveIntegerField(default=60)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default='')
    meeting_link = models.URLField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.mentor.email} - {self.mentee.email}"

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email}: {self.subject}"

class Advertisement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to=advertisement_image_path, blank=True, null=True)
    link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class CollaborationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    proposal = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.organization_name} - {self.status}"

class TrainingSession(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.PositiveIntegerField(default=60)
    max_participants = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    meeting_link = models.URLField(blank=True, null=True, help_text='Meeting link for online sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class TrainingModule(models.Model):
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=30)  # minutes
    recording_url = models.URLField(blank=True, null=True, help_text='YouTube video URL')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.session.title} - {self.title}"

class TrainingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    attended_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'module']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.module.title}"



class TrainingRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'session']
    
    def __str__(self):
        return f"{self.user.email} - {self.session.title}"

class Report(models.Model):
    REPORT_TYPES = [
        ('bug', 'Bug Report'),
        ('content', 'Inappropriate Content'),
        ('user', 'User Behavior'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    admin_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_report_type_display()}: {self.subject}"

class CVReview(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cv_file = models.FileField(upload_to=cv_file_path)
    additional_info = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True, default='')
    score = models.PositiveIntegerField(default=0, help_text='Score out of 100')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cv_reviews_done')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"CV Review for {self.user.email}"

class ApplicationGuidance(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(default='')
    category = models.CharField(max_length=100, default='General')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class InterviewPreparation(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(default='')
    tips = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class ProfileOptimization(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(default='')
    platform = models.CharField(max_length=100, default='General')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class SuccessTip(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(default='')
    category = models.CharField(max_length=100, default='General')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Webinar(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    presenter = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(default=timezone.now)
    meeting_link = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class WebinarRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'webinar']
    
    def __str__(self):
        return f"{self.user.email} - {self.webinar.title}"

class CommunityPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(default='')
    image = models.ImageField(upload_to=community_post_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        content_preview = self.content[:50] if self.content else "No content"
        user_email = self.user.email if self.user else "Anonymous"
        return f"{user_email}: {content_preview}..."

class PostComment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.email}: {self.content[:30]}..."

class PostReaction(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f"{self.user.email} liked {self.post.id}"



class CommunityDiscussion(models.Model):
    TOPIC_CHOICES = [
        ('career-advice', 'Career Advice'),
        ('interview-tips', 'Interview Tips'),
        ('resume-help', 'Resume Help'),
        ('networking', 'Networking'),
        ('success-stories', 'Success Stories'),
    ]
    
    topic = models.CharField(max_length=50, choices=TOPIC_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField(default='')
    is_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class CommunityReply(models.Model):
    discussion = models.ForeignKey(CommunityDiscussion, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField(default='')
    is_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Reply to {self.discussion.title}"

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField(default='')
    excerpt = models.TextField(blank=True, default='')
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    author = models.CharField(max_length=100, default='Youth Opportunities Team')
    author_avatar = models.ImageField(upload_to='author_avatars/', blank=True, null=True)
    category = models.CharField(max_length=50, default='General')
    is_featured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    read_time = models.CharField(max_length=20, default='5 min read')
    created_at = models.DateTimeField(auto_now_add=True)
    published_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class SuccessStory(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField(default='')
    excerpt = models.TextField(blank=True, default='')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    author_location = models.CharField(max_length=100, blank=True, default='')
    featured_image = models.ImageField(upload_to='success_stories/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.title} - {self.author_name}"

class ServiceRequest(models.Model):
    SERVICE_TYPES = [
        ('mentorship', '1-on-1 Mentorship'),
        ('application', 'Application Guidance'),
        ('interview', 'Interview Preparation'),
        ('profile', 'Profile Optimization'),
        ('tips', 'Tips for Success'),
        ('cv', 'CV/Resume Review'),
        ('advertisement', 'Advertisement'),
        ('event', 'Event Promotion'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    people_count = models.PositiveIntegerField(default=1)
    preferred_date = models.DateField(null=True, blank=True)
    link = models.URLField(blank=True, default='')
    file_upload = models.FileField(upload_to='service_files/', blank=True, null=True)
    description = models.TextField(default='')
    additional_info = models.TextField(blank=True, default='')
    contact_info = models.CharField(max_length=200, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.name}"

def tip_file_path(instance, filename):
    return f'tip_files/{instance.category.slug}/{filename}'

class TipCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-lightbulb')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Tip Categories'
    
    def __str__(self):
        return self.name

class Tip(models.Model):
    category = models.ForeignKey(TipCategory, on_delete=models.CASCADE, related_name='tips')
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
    
    def __str__(self):
        return f"{self.category.name}: {self.title}"

class TipFile(models.Model):
    category = models.ForeignKey(TipCategory, on_delete=models.CASCADE, related_name='files')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to=tip_file_path, validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])])
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.category.name}: {self.title}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True, default='')
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f"{self.name} ({self.email})" if self.name else self.email

class TeamMember(models.Model):
    about_section = models.ForeignKey('AboutSection', on_delete=models.CASCADE, related_name='team_members', null=True, blank=True)
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Team Member"
        verbose_name_plural = "About Us - Team Members"
    
    def __str__(self):
        return f"{self.name} - {self.position}"

class Partner(models.Model):
    about_section = models.ForeignKey('AboutSection', on_delete=models.CASCADE, related_name='partners', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    logo = models.ImageField(upload_to='partners/', blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    partnership_type = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Partner"
        verbose_name_plural = "About Us - Partners"
    
    def __str__(self):
        return self.name

class AboutSection(models.Model):
    SECTION_CHOICES = [
        ('who_we_are', 'Who We Are'),
        ('our_mission', 'Our Mission'),
        ('our_vision', 'Our Vision'),
        ('founded_in', 'Founded In'),
        ('what_we_offer', 'What We Offer'),
        ('our_impact', 'Our Impact'),
    ]
    
    section_type = models.CharField(max_length=50, choices=SECTION_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "About Us Section"
        verbose_name_plural = "About Us Management"
    
    def __str__(self):
        return f"{self.get_section_type_display()}: {self.title}"

class HeroSlide(models.Model):
    about_section = models.ForeignKey('AboutSection', on_delete=models.CASCADE, related_name='hero_slides', null=True, blank=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200)
    description = models.CharField(max_length=300)
    image = models.ImageField(upload_to='hero_slides/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Hero Slide"
        verbose_name_plural = "About Us - Hero Slides"
    
    def __str__(self):
        return self.title

class FAQ(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'question']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return self.question

class MentorApplication(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('in_review', 'In Review'),
        ('interview', 'Interview'),
        ('completed', 'Completed'),
        ('successful', 'Successful'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_applications')
    years_experience = models.PositiveIntegerField()
    why_mentor = models.TextField()
    agree_to_terms = models.BooleanField(default=False)
    agree_to_volunteer = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    admin_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.status}"

class InternalDiscussion(models.Model):
    TOPIC_CHOICES = [
        ('general', 'General'),
        ('career', 'Career'),
        ('education', 'Education'),
        ('opportunities', 'Opportunities'),
        ('mentorship', 'Mentorship'),
        ('networking', 'Networking'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='internal_discussions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class InternalDiscussionReply(models.Model):
    discussion = models.ForeignKey(InternalDiscussion, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='internal_replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Reply by {self.user.full_name} on {self.discussion.title}"

class ChatRoom(models.Model):
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    room_type = models.CharField(max_length=50, default='direct')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        participant_names = ', '.join([user.full_name for user in self.participants.all()[:2]])
        return f"Chat: {participant_names}"

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.full_name}: {self.content[:50]}..."
