from django.urls import path
from . import views

app_name = 'enquiries'

urlpatterns = [
    path('contact/', views.contact_view, name='contact'),
    path('request-site-visit/', views.site_visit_request, name='site_visit'),

    # CMS Leads URLs
    path('cms/inbox/', views.cms_enquiry_inbox, name='cms_inbox'),
    path('cms/<int:pk>/', views.cms_enquiry_detail, name='cms_detail'),
]
