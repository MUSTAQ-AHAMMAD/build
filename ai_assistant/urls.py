from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    # Public AJAX Chat Endpoints
    path('api/ai/init/', views.api_chat_init, name='api_init'),
    path('api/ai/message/', views.api_chat_message, name='api_message'),
    path('api/ai/lead-capture/', views.api_chat_lead_capture, name='api_lead_capture'),

    # AI Workspace Root & Aliases
    path('aichatboat/', views.cms_ai_dashboard, name='workspace_root'),
    path('aichatboat/dashboard/', views.cms_ai_dashboard, name='workspace_dashboard'),
    path('aichatboat/conversations/', views.cms_ai_conversations, name='workspace_conversations'),
    path('aichatboat/conversations/<str:session_id>/', views.cms_ai_conversation_detail, name='workspace_conversation_detail'),
    path('aichatboat/settings/', views.cms_ai_settings, name='workspace_settings'),
    path('aichatboat/knowledge/', views.cms_ai_knowledge_base, name='workspace_knowledge_base'),

    # CMS AI Management & Analytics (Backward compatibility)
    path('cms/ai/', views.cms_ai_dashboard, name='cms_dashboard'),
    path('cms/ai/dashboard/', views.cms_ai_dashboard, name='cms_dashboard_alias'),
    path('cms/ai/conversations/', views.cms_ai_conversations, name='cms_conversations'),
    path('cms/ai/conversations/<str:session_id>/', views.cms_ai_conversation_detail, name='cms_conversation_detail'),
    path('cms/ai/settings/', views.cms_ai_settings, name='cms_settings'),
    path('cms/ai/knowledge/', views.cms_ai_knowledge_base, name='cms_knowledge_base'),
]
