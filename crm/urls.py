from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    # CRM Workspace Root & Aliases
    path('crm/', views.crm_dashboard, name='workspace_root'),
    path('crm/dashboard/', views.crm_dashboard, name='workspace_dashboard'),
    path('crm/leads/', views.crm_lead_list, name='workspace_leads'),
    path('crm/leads/create/', views.crm_lead_create, name='workspace_lead_create'),
    path('crm/follow-ups/', views.crm_followup_list, name='workspace_followups'),
    path('crm/site-visits/', views.crm_sitevisit_list, name='workspace_sitevisits'),
    path('crm/estimates/', views.crm_estimate_list, name='workspace_estimates'),
    path('crm/reports/', views.crm_reports, name='workspace_reports'),
    path('crm/settings/', views.crm_settings, name='workspace_settings'),

    # CMS CRM Paths (Backward compatibility)
    path('cms/crm/', views.crm_dashboard, name='dashboard'),
    path('cms/crm/dashboard/', views.crm_dashboard, name='dashboard_alias'),

    # Lead Management
    path('cms/crm/leads/', views.crm_lead_list, name='lead_list'),
    path('cms/crm/leads/create/', views.crm_lead_create, name='lead_create'),
    path('cms/crm/leads/<int:pk>/', views.crm_lead_detail, name='lead_detail'),
    path('cms/crm/leads/<int:pk>/edit/', views.crm_lead_edit, name='lead_edit'),
    path('cms/crm/leads/<int:pk>/delete/', views.crm_lead_delete, name='lead_delete'),
    path('cms/crm/leads/<int:pk>/restore/', views.crm_lead_restore, name='lead_restore'),
    path('cms/crm/leads/<int:pk>/permanent-delete/', views.crm_lead_permanent_delete, name='lead_permanent_delete'),

    # Lead Workflow Actions
    path('cms/crm/leads/<int:pk>/assign/', views.crm_lead_assign, name='lead_assign'),
    path('cms/crm/leads/<int:pk>/won/', views.crm_lead_mark_won, name='lead_mark_won'),
    path('cms/crm/leads/<int:pk>/lost/', views.crm_lead_mark_lost, name='lead_mark_lost'),
    path('cms/crm/leads/<int:pk>/on-hold/', views.crm_lead_on_hold, name='lead_on_hold'),
    path('cms/crm/leads/<int:pk>/notes/', views.crm_lead_note_create, name='lead_note_create'),
    path('cms/crm/leads/<int:pk>/followup/', views.crm_followup_create, name='lead_followup_create'),
    path('cms/crm/leads/<int:pk>/sitevisit/', views.crm_sitevisit_create, name='lead_sitevisit_create'),
    path('cms/crm/leads/<int:pk>/estimate/', views.crm_estimate_create, name='lead_estimate_create'),

    # Communication & Inspection Modules
    path('cms/crm/follow-ups/', views.crm_followup_list, name='followup_list'),
    path('cms/crm/follow-ups/<int:pk>/complete/', views.crm_followup_complete, name='followup_complete'),
    path('cms/crm/site-visits/', views.crm_sitevisit_list, name='sitevisit_list'),
    path('cms/crm/estimates/', views.crm_estimate_list, name='estimate_list'),

    # Reports & Settings
    path('cms/crm/reports/', views.crm_reports, name='reports'),
    path('cms/crm/settings/', views.crm_settings, name='settings'),
]
