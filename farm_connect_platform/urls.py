from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from accounts.views import contact

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include(('admin_panel.urls', 'admin_panel'), namespace='admin_panel')),
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', contact, name='contact'),
    path('faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
    path('help/', TemplateView.as_view(template_name='help.html'), name='help'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
    # Apps
    path('accounts/', include('accounts.urls')),
    path('crops/', include('crops.urls')),
    path('market/', include('market.urls')),
    path('messages/', include('messaging.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler404 = 'farm_connect_platform.views.handler404'
handler500 = 'farm_connect_platform.views.handler500'
