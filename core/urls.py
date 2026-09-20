from django.urls import path
from . import views
from . import portal_views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('how-we-work/', views.how_we_work_view, name='how_we_work'),
    path('faqs/', views.faqs_view, name='faqs'),
    path('contact/', views.contact_view, name='contact'),
    path('get-free-consultation/', views.consultation_view, name='consultation'),
    path('privacy-policy/', views.privacy_view, name='privacy'),
    path('terms-and-conditions/', views.terms_view, name='terms'),
    path('disclaimer/', views.disclaimer_view, name='disclaimer'),
    path('cookie-policy/', views.cookie_policy_view, name='cookie_policy'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('robots.txt', views.robots_txt, name='robots_txt'),

    # CMS Global URLs
    path('cms/login/', views.cms_login, name='cms_login'),
    path('cms/logout/', views.cms_logout, name='cms_logout'),
    path('cms/', views.cms_dashboard, name='cms_dashboard'),
    path('cms/dashboard/', views.cms_dashboard, name='cms_dashboard_alias'),
    path('cms/settings/', views.cms_settings, name='cms_settings'),

    # Customer Portal URLs
    path('portal/register/', portal_views.portal_register, name='portal_register'),
    path('portal/login/', portal_views.portal_login, name='portal_login'),
    path('portal/logout/', portal_views.portal_logout, name='portal_logout'),
    path('portal/', portal_views.portal_dashboard, name='portal_dashboard'),
    path('portal/dashboard/', portal_views.portal_dashboard, name='portal_dashboard_alias'),
    path('portal/projects/', portal_views.portal_projects, name='portal_projects'),
    path('portal/projects/<slug:slug>/', portal_views.portal_project_detail, name='portal_project_detail'),
    path('portal/estimates/', portal_views.portal_estimates, name='portal_estimates'),
    path('portal/proposals/', portal_views.portal_proposals, name='portal_proposals'),
    path('portal/payments/', portal_views.portal_payments, name='portal_payments'),
    path('portal/support/', portal_views.portal_support, name='portal_support'),
    path('portal/support/create/', portal_views.portal_support_create, name='portal_support_create'),
    path('portal/support/<str:ticket_id>/', portal_views.portal_support_detail, name='portal_support_detail'),
]
