from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'core.views.custom_404_view'
handler500 = 'core.views.custom_500_view'
handler403 = 'core.views.custom_403_view'
handler400 = 'core.views.custom_400_view'

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Blog & Knowledge Centre (Public + CMS)
    path('', include('blog.urls')),

    # Dedicated Services URLs
    path('', include('services.urls')),

    # Projects URLs
    path('projects/', include('projects.urls')),

    # CRM & Enquiry Management Portal
    path('', include('crm.urls')),

    # AI Customer Consultant & Interaction Hub
    path('', include('ai_assistant.urls')),

    # Payment Gateway & UPI Management Hub
    path('', include('payments.urls')),

    # Enquiries & Leads URLs (Backward compatibility)
    path('', include('enquiries.urls')),

    # Core & Global CMS Pages
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
