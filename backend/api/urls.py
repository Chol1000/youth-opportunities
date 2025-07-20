from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('csrf/', views.CSRFTokenView.as_view(), name='csrf_token'),
    path('csrf-token/', views.CSRFTokenView.as_view(), name='csrf_token_alt'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('current-user/', views.CurrentUserView.as_view(), name='current_user'),
    path('user/', views.CurrentUserView.as_view(), name='user'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    
    # Profile Management
    path('profile/update/', views.UpdateProfileView.as_view(), name='update_profile'),
    path('profile/preferences/', views.UserPreferencesView.as_view(), name='user_preferences'),
    path('get-preferences/', views.UserPreferencesView.as_view(), name='get_preferences'),
    path('save-preferences/', views.UserPreferencesView.as_view(), name='save_preferences'),
    path('update-profile/', views.UpdateProfileView.as_view(), name='update_profile_alt'),
    path('dashboard-stats/', views.DashboardStatsView.as_view(), name='dashboard_stats_alt'),
    path('profile-activities/', views.NotificationListView.as_view(), name='profile_activities'),
    path('chat/rooms/', views.ChatRoomView.as_view(), name='chat_rooms'),
    path('chat/messages/<int:room_id>/', views.ChatMessageView.as_view(), name='chat_messages'),
    path('chat/messages/<int:room_id>/<int:message_id>/', views.ChatMessageView.as_view(), name='chat_message_detail'),
    path('chat/rooms/user/<int:user_id>/', views.ChatRoomDeleteView.as_view(), name='chat_room_delete'),
    path('users/', views.UsersListView.as_view(), name='users'),
    path('users/<int:user_id>/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('user/activity/', views.UserActivityView.as_view(), name='user_activity'),
    path('profile/view-tracking/', views.ProfileViewTrackingView.as_view(), name='profile_view_tracking'),
    path('my-opportunities/', views.OpportunityView.as_view(), name='my_opportunities'),
    path('mentors/', views.MentorListView.as_view(), name='mentors'),
    path('profile/matching/', views.OpportunityMatchingView.as_view(), name='opportunity_matching'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password_alt'),
    path('profile/deactivate/', views.DeactivateAccountView.as_view(), name='deactivate_account'),
    path('deactivate-account/', views.DeactivateAccountView.as_view(), name='deactivate_account_alt'),
    path('profile/delete/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete_account_alt'),
    
    # Education
    path('education/', views.EducationView.as_view(), name='education_list'),
    path('educations/', views.EducationView.as_view(), name='educations'),
    path('education/<int:pk>/', views.EducationDetailView.as_view(), name='education_detail'),
    path('educations/<int:pk>/', views.EducationDetailView.as_view(), name='educations_detail'),
    
    # Experience
    path('experience/', views.ExperienceView.as_view(), name='experience_list'),
    path('experiences/', views.ExperienceView.as_view(), name='experiences'),
    path('experience/<int:pk>/', views.ExperienceDetailView.as_view(), name='experience_detail'),
    path('experiences/<int:pk>/', views.ExperienceDetailView.as_view(), name='experiences_detail'),
    
    # Documents
    path('documents/', views.UserDocumentView.as_view(), name='user_documents'),
    path('documents/<int:pk>/', views.UserDocumentDetailView.as_view(), name='user_document_detail'),
    
    # Opportunities
    path('opportunities/', views.OpportunityView.as_view(), name='opportunity_list'),
    path('opportunities/<int:opportunity_id>/', views.OpportunityDetailView.as_view(), name='opportunity_detail'),
    path('opportunities/create/', views.CreateOpportunityView.as_view(), name='create_opportunity'),
    path('create-opportunity/', views.CreateOpportunityView.as_view(), name='create_opportunity_alt'),
    path('opportunities/public-submit/', views.PublicOpportunitySubmissionView.as_view(), name='public_opportunity_submit'),
    path('opportunities/<int:opportunity_id>/status/', views.UpdateOpportunityStatusView.as_view(), name='update_opportunity_status'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.MarkNotificationAsReadView.as_view(), name='mark_notification_read'),
    path('notifications/mark-all-read/', views.MarkAllNotificationsAsReadView.as_view(), name='mark_all_notifications_read'),
    
    # Mentorship
    path('mentorship/requests/', views.MentorRequestView.as_view(), name='mentor_request_list'),
    path('mentorship/requests/<int:request_id>/', views.MentorRequestDetailView.as_view(), name='mentor_request_detail'),
    path('mentorship/requests/<int:request_id>/status/', views.UpdateMentorRequestStatusView.as_view(), name='update_mentor_request_status'),
    path('mentorship/sessions/', views.MentorshipSessionView.as_view(), name='mentorship_session_list'),
    path('mentorship/sessions/request/', views.MentorshipSessionRequestView.as_view(), name='mentorship_session_request'),
    path('mentorship/sessions/<int:session_id>/', views.MentorshipSessionView.as_view(), name='mentorship_session_detail'),
    
    # Feedback
    path('feedback/', views.FeedbackView.as_view(), name='feedback'),
    
    # Advertisements
    path('advertisements/', views.AdvertisementView.as_view(), name='advertisement_list'),
    path('advertisements/create/', views.CreateAdvertisementView.as_view(), name='create_advertisement'),
    
    # Collaboration
    path('collaboration/', views.CollaborationRequestView.as_view(), name='collaboration_request'),
    path('collaboration/<int:request_id>/status/', views.UpdateCollaborationRequestStatusView.as_view(), name='update_collaboration_status'),
    
    # Training
    path('training/', views.TrainingSessionView.as_view(), name='training_session_list'),
    path('my-training-registrations/', views.MyTrainingRegistrationsView.as_view(), name='my_training_registrations'),
    path('training-sessions/', views.TrainingSessionView.as_view(), name='training_sessions'),
    path('training/<int:session_id>/register/', views.RegisterForTrainingView.as_view(), name='register_training'),
    path('training-sessions/<int:session_id>/register/', views.RegisterForTrainingView.as_view(), name='register_training_sessions'),
    path('training-sessions/<int:session_id>/unregister/', views.UnregisterFromTrainingView.as_view(), name='unregister_training'),
    
    # Reports
    path('reports/', views.ReportView.as_view(), name='report_list'),
    path('reports/<int:report_id>/status/', views.UpdateReportStatusView.as_view(), name='update_report_status'),
    
    # CV Review
    path('cv-review/', views.CVReviewView.as_view(), name='cv_review'),
    path('cv-reviews/', views.CVReviewView.as_view(), name='cv_reviews'),

    path('cv-review/<int:review_id>/', views.UpdateCVReviewView.as_view(), name='update_cv_review'),
    
    # Guidance
    path('guidance/application/', views.ApplicationGuidanceView.as_view(), name='application_guidance'),
    path('guidance/interview/', views.InterviewPreparationView.as_view(), name='interview_preparation'),
    path('guidance/profile/', views.ProfileOptimizationView.as_view(), name='profile_optimization'),
    path('guidance/tips/', views.SuccessTipView.as_view(), name='success_tips'),
    
    # Webinars
    path('webinars/', views.WebinarView.as_view(), name='webinar_list'),
    path('webinar-registrations/', views.WebinarRegistrationView.as_view(), name='webinar_registrations'),
    path('my-webinar-registrations/', views.MyWebinarRegistrationsView.as_view(), name='my_webinar_registrations'),
    path('webinars/<int:webinar_id>/register/', views.RegisterForWebinarView.as_view(), name='register_webinar'),
    path('webinars/<int:webinar_id>/unregister/', views.UnregisterFromWebinarView.as_view(), name='unregister_webinar'),
    path('webinars/<int:webinar_id>/register/', views.RegisterForWebinarView.as_view(), name='register_webinar'),
    
    # Community
    path('community/posts/', views.CommunityPostView.as_view(), name='community_post_list'),
    path('community/posts/<int:post_id>/', views.CommunityPostDetailView.as_view(), name='community_post_detail'),
    path('community/posts/<int:post_id>/comments/', views.PostCommentView.as_view(), name='post_comment'),
    path('community/posts/<int:post_id>/reactions/', views.PostReactionView.as_view(), name='post_reaction'),
    path('community/comments/<int:comment_id>/', views.CommentDetailView.as_view(), name='comment_detail'),
    path('community/comments/<int:comment_id>/reactions/', views.CommentReactionView.as_view(), name='comment_reaction'),
    
    # Community Topics and Discussions
    path('community/topics/', views.CommunityTopicsView.as_view(), name='community_topics'),
    path('community/discussions/', views.CommunityDiscussionsView.as_view(), name='community_discussions'),
    path('community/discussions/<int:discussion_id>/', views.CommunityDiscussionDetailView.as_view(), name='community_discussion_detail'),
    path('community/discussions/<int:discussion_id>/replies/', views.CommunityDiscussionRepliesView.as_view(), name='community_discussion_replies'),
    path('community/replies/<int:reply_id>/', views.CommunityReplyDetailView.as_view(), name='community_reply_detail'),
    
    # User Management (Admin)
    path('admin/users/', views.UserManagementView.as_view(), name='user_management'),
    path('admin/users/<int:user_id>/role/', views.UpdateUserRoleView.as_view(), name='update_user_role'),
    path('admin/users/<int:user_id>/ban/', views.BanUserView.as_view(), name='ban_user'),
    path('admin/users/<int:user_id>/unban/', views.UnbanUserView.as_view(), name='unban_user'),
    
    # Dashboard
    path('admin/dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard_stats'),
    
    # Services
    path('services/request/', views.ServiceRequestView.as_view(), name='service_request'),
    
    # Mentor Applications
    path('mentor-applications/', views.MentorApplicationView.as_view(), name='mentor_applications'),
    
    # Internal Discussions
    path('internal-discussions/', views.InternalDiscussionView.as_view(), name='internal_discussions'),
    path('internal-discussions/<int:discussion_id>/', views.InternalDiscussionDetailView.as_view(), name='internal_discussion_detail'),
    path('internal-discussions/<int:discussion_id>/replies/', views.InternalDiscussionRepliesView.as_view(), name='internal_discussion_replies'),
    path('internal-discussions/replies/<int:reply_id>/', views.InternalDiscussionReplyDetailView.as_view(), name='internal_discussion_reply_detail'),
    
    # Blogs
    path('blogs/', views.BlogPostView.as_view(), name='blog_posts'),
    path('success-stories/submit/', views.SuccessStorySubmissionView.as_view(), name='success_story_submit'),
    path('blog-toolkit/', views.BlogToolkitView.as_view(), name='blog_toolkit'),
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    path('faq/', views.faq_view, name='faq'),
]
