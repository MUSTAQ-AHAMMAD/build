from django.contrib import admin
from .models import ChatSession, ChatMessage, AIChatbotSettings, AIKnowledgeItem

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['sender_type', 'sender_name', 'content', 'quick_actions_json', 'created_at']
    can_delete = False

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'visitor_name', 'visitor_phone', 'service_category', 'status', 'suggested_priority', 'human_agent_active', 'last_activity_at']
    list_filter = ['status', 'suggested_priority', 'service_category', 'human_agent_active', 'is_nri']
    search_fields = ['session_id', 'visitor_name', 'visitor_phone', 'visitor_email', 'visitor_location', 'detected_intent']
    readonly_fields = ['session_id', 'started_at', 'last_activity_at', 'ip_address', 'user_agent']
    inlines = [ChatMessageInline]

@admin.register(AIChatbotSettings)
class AIChatbotSettingsAdmin(admin.ModelAdmin):
    list_display = ['ai_name', 'is_enabled', 'contact_phone', 'whatsapp_number', 'updated_at']

@admin.register(AIKnowledgeItem)
class AIKnowledgeItemAdmin(admin.ModelAdmin):
    list_display = ['topic', 'category', 'is_active', 'display_order', 'updated_at']
    list_filter = ['category', 'is_active']
    search_fields = ['topic', 'keywords', 'approved_content']
