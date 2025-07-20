from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import never_cache
from api.views import CSRFTokenView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/csrf/', CSRFTokenView.as_view(), name='csrf_token'),
    path('api/', include('api.urls')),
    
    # Frontend HTML files
    re_path(r'^reset_password\.html$', TemplateView.as_view(template_name='reset_password.html')),
    re_path(r'^login\.html$', TemplateView.as_view(template_name='login.html')),
    re_path(r'^register\.html$', TemplateView.as_view(template_name='register.html')),
    
    # Dashboard paths
    re_path(r'^admin_dashboard/index\.html$', TemplateView.as_view(template_name='admin_dashboard/index.html')),
    re_path(r'^user_dashboard/index\.html$', TemplateView.as_view(template_name='user_dashboard/index.html')),
    re_path(r'^user_dashboard/profile\.html$', TemplateView.as_view(template_name='user_dashboard/profile.html')),
    re_path(r'^user_dashboard/opportunities\.html$', TemplateView.as_view(template_name='user_dashboard/opportunities.html')),
    re_path(r'^user_dashboard/mentors\.html$', TemplateView.as_view(template_name='user_dashboard/mentors.html')),
    re_path(r'^user_dashboard/community\.html$', TemplateView.as_view(template_name='user_dashboard/community.html')),
    re_path(r'^user_dashboard/inbox\.html$', TemplateView.as_view(template_name='user_dashboard/inbox.html')),
    re_path(r'^user_dashboard/cv-review\.html$', TemplateView.as_view(template_name='user_dashboard/cv-review.html')),
    re_path(r'^user_dashboard/training\.html$', TemplateView.as_view(template_name='user_dashboard/training.html')),
    re_path(r'^user_dashboard/webinars\.html$', TemplateView.as_view(template_name='user_dashboard/webinars.html')),
    re_path(r'^user_dashboard/notifications\.html$', TemplateView.as_view(template_name='user_dashboard/notifications.html')),
    re_path(r'^user_dashboard/settings\.html$', TemplateView.as_view(template_name='user_dashboard/settings.html')),
    re_path(r'^user_dashboard/opportunity-details\.html$', TemplateView.as_view(template_name='user_dashboard/opportunity-details.html')),
    re_path(r'^user_dashboard/profile-view\.html$', TemplateView.as_view(template_name='user_dashboard/profile-view.html')),
    re_path(r'^user_dashboard/inbox\.html$', TemplateView.as_view(template_name='inbox.html')),
    
    # Posts pages
    re_path(r'^posts/home\.html$', TemplateView.as_view(template_name='posts/home.html')),
    re_path(r'^posts/jobs\.html$', TemplateView.as_view(template_name='posts/jobs.html')),
    re_path(r'^posts/jobs-complete\.html$', TemplateView.as_view(template_name='posts/jobs-complete.html')),
    re_path(r'^posts/internships\.html$', TemplateView.as_view(template_name='posts/internships.html')),
    re_path(r'^posts/scholarships\.html$', TemplateView.as_view(template_name='posts/scholarships.html')),
    re_path(r'^posts/grants\.html$', TemplateView.as_view(template_name='posts/grants.html')),
    re_path(r'^posts/fellowships\.html$', TemplateView.as_view(template_name='posts/fellowships.html')),
    re_path(r'^posts/conferences\.html$', TemplateView.as_view(template_name='posts/conferences.html')),
    re_path(r'^posts/workshops\.html$', TemplateView.as_view(template_name='posts/workshops.html')),
    re_path(r'^posts/trainings\.html$', TemplateView.as_view(template_name='posts/trainings.html')),
    re_path(r'^posts/competitions\.html$', TemplateView.as_view(template_name='posts/competitions.html')),
    re_path(r'^posts/community\.html$', TemplateView.as_view(template_name='posts/community.html')),
    re_path(r'^posts/blogs\.html$', TemplateView.as_view(template_name='posts/blogs.html')),
    re_path(r'^posts/faq\.html$', TemplateView.as_view(template_name='posts/faq.html')),
    re_path(r'^posts/success-stories\.html$', TemplateView.as_view(template_name='posts/success-stories.html')),
    re_path(r'^posts/full-story\.html$', TemplateView.as_view(template_name='posts/full-story.html')),
    re_path(r'^posts/services\.html$', TemplateView.as_view(template_name='posts/services.html')),
    re_path(r'^posts/announcements\.html$', TemplateView.as_view(template_name='posts/announcements.html')),
    re_path(r'^posts/miscellaneous\.html$', TemplateView.as_view(template_name='posts/miscellaneous.html')),
    re_path(r'^posts/aboutus\.html$', TemplateView.as_view(template_name='posts/aboutus.html')),
    re_path(r'^posts/shareopportunity\.html$', TemplateView.as_view(template_name='posts/shareopportunity.html')),
    re_path(r'^posts/share-opportunity\.html$', TemplateView.as_view(template_name='posts/share-opportunity.html')),
    re_path(r'^posts/opportunity-details\.html$', TemplateView.as_view(template_name='posts/opportunity-details.html')),
    re_path(r'^posts/featured\.html$', TemplateView.as_view(template_name='posts/featured.html')),
    re_path(r'^posts/featured-internships\.html$', TemplateView.as_view(template_name='posts/featured-internships.html')),
    re_path(r'^posts/featured-jobs\.html$', TemplateView.as_view(template_name='posts/featured-jobs.html')),
    re_path(r'^posts/featured-grants\.html$', TemplateView.as_view(template_name='posts/featured-grants.html')),
    re_path(r'^posts/featured-scholarships\.html$', TemplateView.as_view(template_name='posts/featured-scholarships.html')),
    re_path(r'^posts/featured-fellowships\.html$', TemplateView.as_view(template_name='posts/featured-fellowships.html')),
    re_path(r'^posts/featured-workshops\.html$', TemplateView.as_view(template_name='posts/featured-workshops.html')),
    re_path(r'^posts/featured-conferences\.html$', TemplateView.as_view(template_name='posts/featured-conferences.html')),
    re_path(r'^posts/featured-trainings\.html$', TemplateView.as_view(template_name='posts/featured-trainings.html')),
    re_path(r'^posts/featured-competitions\.html$', TemplateView.as_view(template_name='posts/featured-competitions.html')),
    re_path(r'^posts/featured-announcements\.html$', TemplateView.as_view(template_name='posts/featured-announcements.html')),
    re_path(r'^posts/featured-miscellaneous\.html$', TemplateView.as_view(template_name='posts/featured-miscellaneous.html')),
    
    # Other pages
    re_path(r'^mentorship\.html$', TemplateView.as_view(template_name='mentorship.html')),
    re_path(r'^cv_review\.html$', TemplateView.as_view(template_name='cv_review.html')),
    re_path(r'^support\.html$', TemplateView.as_view(template_name='support.html')),

    
    # Favicon
    re_path(r'^favicon\.ico$', never_cache(serve), {'path': 'images/favicon.ico'}),
    
    # Homepage
    re_path(r'^$', TemplateView.as_view(template_name='index.html')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
