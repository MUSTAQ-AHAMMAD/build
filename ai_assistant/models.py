import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from crm.models import Lead

class AIChatbotSettings(models.Model):
    """Singleton configuration for the AI Customer Consultant"""
    is_enabled = models.BooleanField(default=True, help_text="Master toggle for public AI chatbot")
    ai_name = models.CharField(max_length=100, default="BUILD+ AI Consultant")
    welcome_message = models.TextField(
        default="Hello! I'm your AI Construction & Property Consultant. How can I assist with your project today?"
    )
    business_description = models.TextField(
        default="BUILD+ specializes in Construction, Flat & Apartment Renovation, Demolition, Reconstruction, Society Redevelopment, Property/Land Due Diligence, and NRI Property Stewardship."
    )
    contact_phone = models.CharField(max_length=50, default="+91 98765 43210")
    whatsapp_number = models.CharField(max_length=50, default="+91 98765 43210")
    working_hours = models.CharField(max_length=150, default="Mon - Sat: 9:00 AM - 7:30 PM IST")
    emergency_message = models.TextField(
        default="For urgent site safety or structural concerns, please contact our senior engineering team directly via phone or WhatsApp."
    )
    fallback_message = models.TextField(
        default="I apologize, but I couldn't process that. Would you like me to connect you with our engineering staff or help you submit an enquiry?"
    )
    human_handoff_message = models.TextField(
        default="I am connecting you with our senior customer consulting desk. A representative will take over or follow up with you shortly."
    )
    enable_lead_capture = models.BooleanField(default=True)
    enable_ai_summary = models.BooleanField(default=True)
    enable_ai_priority = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Chatbot Settings"
        verbose_name_plural = "AI Chatbot Settings"

    def __str__(self):
        return f"{self.ai_name} Settings ({'Enabled' if self.is_enabled else 'Disabled'})"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AIKnowledgeItem(models.Model):
    """Approved Knowledge Base for grounded AI responses"""
    CATEGORY_CHOICES = [
        ('construction', 'New Construction (Houses, Villas, Commercial)'),
        ('renovation', 'Flat & Apartment Renovation (Resale, Damaged, Structural)'),
        ('demolition', 'Controlled Demolition & Site Clearance'),
        ('reconstruction', 'Structural Reconstruction & Rebuilding'),
        ('redevelopment', 'Property & Society Redevelopment'),
        ('property_land', 'Property & Land Advisory'),
        ('nri_services', 'NRI Property Stewardship & Supervision'),
        ('finance', 'Construction & Renovation Loans Guidance'),
        ('policy', 'Company Policies & Working Process'),
    ]

    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, db_index=True)
    topic = models.CharField(max_length=200, help_text="e.g. 20-Year Old Resale Flat Plumbing Replacement")
    keywords = models.CharField(max_length=255, help_text="Comma-separated trigger keywords (e.g. plumbing, GI pipes, leakage, seepage)")
    approved_content = models.TextField(help_text="Factual, engineering-approved guidance for the AI to provide")
    who_is_it_for = models.CharField(max_length=255, blank=True, help_text="e.g. Buyers of older apartments built before 2005")
    typical_process = models.TextField(blank=True, help_text="Step-by-step engineering roadmap")
    pricing_guideline = models.CharField(max_length=255, blank=True, help_text="Explain cost factors (never give fixed fake quotes)")
    safety_boundary = models.CharField(max_length=255, blank=True, help_text="e.g. Must require on-site civil structural inspection")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'display_order', 'topic']
        verbose_name = "AI Knowledge Snippet"
        verbose_name_plural = "AI Knowledge Base"

    def __str__(self):
        return f"[{self.get_category_display()}] {self.topic}"


class ChatSession(models.Model):
    """Represents a visitor conversation session with the AI Assistant"""
    STATUS_CHOICES = [
        ('active', 'Active Conversation'),
        ('completed', 'Completed'),
        ('lead_created', 'Lead Converted'),
        ('human_handoff', 'Human Handoff Requested'),
        ('human_active', 'Human Agent Active'),
        ('abandoned', 'Abandoned / Idle'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('HIGH', 'High Priority'),
        ('URGENT', 'Urgent / Immediate Action'),
    ]

    session_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4, db_index=True)
    
    # Visitor Collected Information
    visitor_name = models.CharField(max_length=150, blank=True)
    visitor_phone = models.CharField(max_length=50, blank=True)
    visitor_email = models.EmailField(blank=True)
    visitor_whatsapp = models.CharField(max_length=50, blank=True)
    visitor_location = models.CharField(max_length=150, blank=True)
    
    # Project Qualification
    service_category = models.CharField(max_length=60, blank=True)
    service_type = models.CharField(max_length=100, blank=True)
    property_type = models.CharField(max_length=100, blank=True)
    property_condition = models.CharField(max_length=100, blank=True)
    approximate_area = models.CharField(max_length=100, blank=True)
    project_description = models.TextField(blank=True)
    estimated_budget = models.CharField(max_length=100, blank=True)
    timeline = models.CharField(max_length=100, blank=True)
    is_nri = models.BooleanField(default=False)
    site_visit_requested = models.BooleanField(default=False)
    preferred_site_visit_date = models.DateField(null=True, blank=True)

    # AI Analysis & Intent
    detected_intent = models.CharField(max_length=150, blank=True, help_text="AI classified intent")
    ai_lead_summary = models.TextField(blank=True, help_text="AI synthesized summary for sales team")
    suggested_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    # CRM & Staff Handover
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active', db_index=True)
    human_agent_active = models.BooleanField(default=False)
    assigned_human_agent = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_chat_sessions'
    )
    lead = models.ForeignKey(
        Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_chat_sessions'
    )

    # Timestamps & Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_activity_at']
        verbose_name = "AI Chat Session"
        verbose_name_plural = "AI Chat Sessions"

    def __str__(self):
        name = self.visitor_name or "Anonymous Visitor"
        service = self.service_category or self.detected_intent or "General Inquiry"
        return f"[{self.get_status_display()}] {name} ({service})"

    @property
    def messages_count(self):
        return self.messages.count()


class ChatMessage(models.Model):
    """Individual message bubbles within an AI conversation"""
    SENDER_CHOICES = [
        ('ai', 'AI Consultant'),
        ('user', 'Customer / Visitor'),
        ('human_agent', 'Staff Representative'),
        ('system', 'System Notice'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=20, choices=SENDER_CHOICES, default='ai')
    sender_name = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    quick_actions_json = models.JSONField(
        default=list, blank=True, help_text="Interactive button pills shown beneath AI message"
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

    def __str__(self):
        return f"{self.get_sender_type_display()} @ {self.created_at.strftime('%H:%M:%S')}: {self.content[:40]}"
