import json
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from .models import ChatSession, ChatMessage, AIChatbotSettings, AIKnowledgeItem
from .gemini_service import AIConsultantEngine
from crm.models import Lead, LeadSource, LeadActivity, SiteVisit

def staff_required(user):
    return user.is_active and user.is_staff


# ==============================================================================
# PUBLIC AI CHATBOT AJAX API
# ==============================================================================

@ensure_csrf_cookie
def api_chat_init(request):
    """Initializes a new or resumes an existing AI chat session"""
    settings = AIChatbotSettings.load()
    if not settings.is_enabled:
        return JsonResponse({'status': 'disabled', 'message': 'AI Chat is currently offline.'})

    session_id = request.GET.get('session_id') or request.POST.get('session_id')
    session = None

    if session_id:
        session = ChatSession.objects.filter(session_id=session_id).first()

    if not session:
        session_id = str(uuid.uuid4())
        session = ChatSession.objects.create(
            session_id=session_id,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:250]
        )
        # Create initial welcome message
        welcome_actions = [
            {"label": "Renovate a Flat / Apartment", "action": "send_msg:I want to renovate my flat", "type": "quick_reply"},
            {"label": "Build a New Property", "action": "send_msg:I am planning a new construction project", "type": "quick_reply"},
            {"label": "Demolition & Reconstruction", "action": "send_msg:Need building demolition and rebuilding", "type": "quick_reply"},
            {"label": "Society Redevelopment", "action": "send_msg:Inquiring about society redevelopment", "type": "quick_reply"},
            {"label": "NRI Property Services", "action": "send_msg:I am an NRI looking for property management", "type": "quick_reply"},
            {"label": "Talk to an Engineer", "action": "send_msg:I want to speak with an engineer", "type": "quick_reply"}
        ]
        ChatMessage.objects.create(
            session=session,
            sender_type='ai',
            sender_name=settings.ai_name,
            content=settings.welcome_message,
            quick_actions_json=welcome_actions
        )

    # Fetch message history
    messages_data = []
    for msg in session.messages.all():
        messages_data.append({
            'id': msg.id,
            'sender': msg.sender_type,
            'sender_name': msg.sender_name or ('AI Consultant' if msg.sender_type == 'ai' else 'You'),
            'content': msg.content,
            'quick_actions': msg.quick_actions_json,
            'created_at': msg.created_at.strftime('%H:%M'),
        })

    return JsonResponse({
        'status': 'ok',
        'session_id': session.session_id,
        'ai_name': settings.ai_name,
        'human_agent_active': session.human_agent_active,
        'messages': messages_data,
        'extracted_data': {
            'name': session.visitor_name,
            'phone': session.visitor_phone,
            'service': session.service_category,
            'location': session.visitor_location,
            'area': session.approximate_area,
            'budget': session.estimated_budget,
            'timeline': session.timeline,
        }
    })


@csrf_exempt
def api_chat_message(request):
    """Processes user message and responds via AI Consultant Engine"""
    if request.method != 'POST':
        return HttpResponseBadRequest("POST required")

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    session_id = data.get('session_id')
    user_message = data.get('message', '').strip()

    if not session_id or not user_message:
        return JsonResponse({'status': 'error', 'message': 'Session ID and message required'}, status=400)

    session = get_object_or_404(ChatSession, session_id=session_id)
    settings = AIChatbotSettings.load()

    # 1. Log User Message
    ChatMessage.objects.create(
        session=session,
        sender_type='user',
        sender_name=session.visitor_name or 'Visitor',
        content=user_message
    )

    # If Human Agent is active on this session, notify staff without AI overwrite
    if session.human_agent_active:
        return JsonResponse({
            'status': 'human_active',
            'session_id': session.session_id,
            'message': 'A staff representative has taken over and will respond shortly.',
            'quick_actions': [
                {"label": "Call Helpline", "action": "tel:+919876543210", "type": "link"},
                {"label": "WhatsApp Support", "action": "https://wa.me/919876543210", "type": "link"}
            ]
        })

    # 2. Generate AI Reply
    reply_text, quick_actions, extracted_info = AIConsultantEngine.generate_reply(session, user_message)

    # 3. Log AI Response
    ai_msg = ChatMessage.objects.create(
        session=session,
        sender_type='ai',
        sender_name=settings.ai_name,
        content=reply_text,
        quick_actions_json=quick_actions
    )

    return JsonResponse({
        'status': 'ok',
        'session_id': session.session_id,
        'reply': {
            'id': ai_msg.id,
            'sender': 'ai',
            'sender_name': settings.ai_name,
            'content': ai_msg.content,
            'quick_actions': ai_msg.quick_actions_json,
            'created_at': ai_msg.created_at.strftime('%H:%M')
        },
        'extracted_data': {
            'name': session.visitor_name,
            'phone': session.visitor_phone,
            'service': session.service_category,
            'location': session.visitor_location,
            'area': session.approximate_area,
            'budget': session.estimated_budget,
            'timeline': session.timeline,
            'site_visit_requested': session.site_visit_requested,
            'summary': session.ai_lead_summary,
        }
    })


@csrf_exempt
def api_chat_lead_capture(request):
    """Captures lead from AI Chatbot into CRM"""
    if request.method != 'POST':
        return HttpResponseBadRequest("POST required")

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    session_id = data.get('session_id')
    session = get_object_or_404(ChatSession, session_id=session_id)

    # Update session visitor info
    name = data.get('name') or session.visitor_name or 'AI Chat Visitor'
    phone = data.get('phone') or session.visitor_phone or ''
    email = data.get('email') or session.visitor_email or ''
    location = data.get('location') or session.visitor_location or 'Unspecified'
    service_cat = data.get('service_category') or session.service_category or 'renovation'
    service_type = data.get('service_type') or session.service_type or 'flat_renovation'
    property_type = data.get('property_type') or session.property_type or 'Apartment / Flat'
    area = data.get('approximate_area') or session.approximate_area or ''
    budget = data.get('budget') or session.estimated_budget or ''
    timeline = data.get('timeline') or session.timeline or ''
    site_visit = data.get('site_visit_requested', False) or session.site_visit_requested

    session.visitor_name = name
    session.visitor_phone = phone
    session.visitor_email = email
    session.visitor_location = location
    session.service_category = service_cat
    session.service_type = service_type
    session.property_type = property_type
    session.approximate_area = area
    session.estimated_budget = budget
    session.timeline = timeline
    session.site_visit_requested = site_visit
    session.status = 'lead_created'

    # 1. Get or Create LeadSource 'AI Chatbot'
    source, _ = LeadSource.objects.get_or_create(name='AI Chatbot')

    # 2. Create CRM Lead
    name_parts = name.strip().split(' ', 1)
    f_name = name_parts[0]
    l_name = name_parts[1] if len(name_parts) > 1 else ''

    lead = Lead.objects.create(
        first_name=f_name,
        last_name=l_name,
        phone=phone or '+91 00000 00000',
        email=email,
        city=location,
        property_location=location,
        lead_source=source,
        lead_source_text='AI Chatbot',
        service_category=service_cat if service_cat in [c[0] for c in Lead.SERVICE_CATEGORIES] else 'renovation',
        service_type=service_type if service_type in [t[0] for t in Lead.SERVICE_TYPES] else 'flat_renovation',
        property_type='flat' if 'flat' in property_type.lower() or 'apartment' in property_type.lower() else 'independent_house',
        approximate_property_area=area,
        estimated_budget=budget,
        priority=session.suggested_priority,
        status='SITE_VISIT' if site_visit else 'NEW',
        project_description=f"AI Chat Inquiry: {service_type}. Location: {location}."
    )

    # Add AI Note
    from crm.models import LeadNote
    LeadNote.objects.create(
        lead=lead,
        note=f"AI Generated Summary:\n{session.ai_lead_summary or 'Inquiry submitted through AI Chatbot.'}"
    )

    # 3. Create SiteVisit record if requested
    if site_visit:
        SiteVisit.objects.create(
            lead=lead,
            visit_date=timezone.now().date(),
            site_address=f"{property_type}, {location} (Area: {area})",
            notes="Automated booking via AI Chatbot Consultation."
        )

    # 4. Create LeadActivity
    LeadActivity.objects.create(
        lead=lead,
        activity_type='created',
        title=f"AI Chatbot Lead Created ({session.session_id[:8]})",
        description=f"Visitor {name} converted from AI Assistant conversation. Service: {service_cat}, Location: {location}."
    )

    session.lead = lead
    session.save()

    # Log system notice in chat
    ChatMessage.objects.create(
        session=session,
        sender_type='system',
        content=f"Project details submitted successfully! Reference Lead ID: {lead.lead_id}. Our engineering team will contact you shortly."
    )

    return JsonResponse({
        'status': 'ok',
        'lead_id': lead.lead_id,
        'message': 'Thank you! Your project consultation request has been registered in our system.'
    })


# ==============================================================================
# CMS / ADMIN VIEWS (AI DASHBOARD & CONVERSATION MANAGEMENT)
# ==============================================================================

@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_ai_dashboard(request):
    """Central AI CRM Analytics & Intelligence Command Center"""
    total_conversations = ChatSession.objects.count()
    leads_created = ChatSession.objects.filter(lead__isnull=False).count()
    site_visits_count = ChatSession.objects.filter(site_visit_requested=True).count()
    human_handoffs = ChatSession.objects.filter(status__in=['human_handoff', 'human_active']).count()
    active_now = ChatSession.objects.filter(status='active').count()

    conversion_rate = round((leads_created / total_conversations * 100), 1) if total_conversations > 0 else 0

    # Service Demand Breakdown
    service_demand = (
        ChatSession.objects.exclude(service_category='')
        .values('service_category')
        .annotate(count=Count('id'))
        .order_by('-count')[:6]
    )

    # Recent AI Sessions
    recent_sessions = ChatSession.objects.select_related('lead', 'assigned_human_agent')[:10]

    context = {
        'total_conversations': total_conversations,
        'leads_created': leads_created,
        'site_visits_count': site_visits_count,
        'human_handoffs': human_handoffs,
        'active_now': active_now,
        'conversion_rate': conversion_rate,
        'service_demand': service_demand,
        'recent_sessions': recent_sessions,
    }
    return render(request, 'ai_assistant/dashboard.html', context)


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_ai_conversations(request):
    """Directory of all customer AI conversation threads"""
    status_filter = request.GET.get('status', 'all')
    search_q = request.GET.get('q', '').strip()

    sessions = ChatSession.objects.select_related('lead', 'assigned_human_agent').all()

    if status_filter == 'active':
        sessions = sessions.filter(status='active')
    elif status_filter == 'converted':
        sessions = sessions.filter(lead__isnull=False)
    elif status_filter == 'human_handoff':
        sessions = sessions.filter(status__in=['human_handoff', 'human_active'])
    elif status_filter == 'abandoned':
        sessions = sessions.filter(status='abandoned')

    if search_q:
        sessions = sessions.filter(
            Q(visitor_name__icontains=search_q) |
            Q(visitor_phone__icontains=search_q) |
            Q(visitor_location__icontains=search_q) |
            Q(detected_intent__icontains=search_q) |
            Q(service_category__icontains=search_q)
        )

    context = {
        'sessions': sessions[:50],
        'status_filter': status_filter,
        'search_q': search_q,
        'total_count': sessions.count()
    }
    return render(request, 'ai_assistant/conversation_list.html', context)


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_ai_conversation_detail(request, session_id):
    """360° Conversation detail view with manual takeover and reply box"""
    session = get_object_or_404(ChatSession, session_id=session_id)
    chat_messages = session.messages.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_takeover':
            session.human_agent_active = not session.human_agent_active
            session.assigned_human_agent = request.user if session.human_agent_active else None
            session.status = 'human_active' if session.human_agent_active else 'active'
            session.save()
            messages.success(request, f"Human Takeover {'Activated' if session.human_agent_active else 'Deactivated'}.")
            return redirect('ai_assistant:cms_conversation_detail', session_id=session.session_id)

        elif action == 'send_manual_reply':
            reply_text = request.POST.get('manual_reply', '').strip()
            if reply_text:
                ChatMessage.objects.create(
                    session=session,
                    sender_type='human_agent',
                    sender_name=request.user.get_full_name() or request.user.username,
                    content=reply_text
                )
                session.last_activity_at = timezone.now()
                session.save(update_fields=['last_activity_at'])
                messages.success(request, "Manual response sent to visitor chat.")
                return redirect('ai_assistant:cms_conversation_detail', session_id=session.session_id)

    context = {
        'session_obj': session,
        'chat_messages': chat_messages,
    }
    return render(request, 'ai_assistant/conversation_detail.html', context)


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_ai_settings(request):
    """CMS Configuration for AI Assistant Parameters"""
    settings_obj = AIChatbotSettings.load()

    if request.method == 'POST':
        settings_obj.is_enabled = request.POST.get('is_enabled') == 'on'
        settings_obj.ai_name = request.POST.get('ai_name', settings_obj.ai_name)
        settings_obj.welcome_message = request.POST.get('welcome_message', settings_obj.welcome_message)
        settings_obj.business_description = request.POST.get('business_description', settings_obj.business_description)
        settings_obj.contact_phone = request.POST.get('contact_phone', settings_obj.contact_phone)
        settings_obj.whatsapp_number = request.POST.get('whatsapp_number', settings_obj.whatsapp_number)
        settings_obj.working_hours = request.POST.get('working_hours', settings_obj.working_hours)
        settings_obj.emergency_message = request.POST.get('emergency_message', settings_obj.emergency_message)
        settings_obj.fallback_message = request.POST.get('fallback_message', settings_obj.fallback_message)
        settings_obj.human_handoff_message = request.POST.get('human_handoff_message', settings_obj.human_handoff_message)
        settings_obj.enable_lead_capture = request.POST.get('enable_lead_capture') == 'on'
        settings_obj.enable_ai_summary = request.POST.get('enable_ai_summary') == 'on'
        settings_obj.enable_ai_priority = request.POST.get('enable_ai_priority') == 'on'
        settings_obj.save()

        messages.success(request, "AI Assistant settings updated successfully.")
        return redirect('ai_assistant:cms_settings')

    return render(request, 'ai_assistant/settings.html', {'settings': settings_obj})


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_ai_knowledge_base(request):
    """Knowledge base manager for grounded AI factual replies"""
    items = AIKnowledgeItem.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            AIKnowledgeItem.objects.create(
                category=request.POST.get('category', 'renovation'),
                topic=request.POST.get('topic', ''),
                keywords=request.POST.get('keywords', ''),
                approved_content=request.POST.get('approved_content', ''),
                who_is_it_for=request.POST.get('who_is_it_for', ''),
                typical_process=request.POST.get('typical_process', ''),
                pricing_guideline=request.POST.get('pricing_guideline', ''),
                safety_boundary=request.POST.get('safety_boundary', ''),
                is_active=request.POST.get('is_active') == 'on'
            )
            messages.success(request, "New knowledge snippet added.")
            return redirect('ai_assistant:cms_knowledge_base')

        elif action == 'delete':
            item_id = request.POST.get('item_id')
            item = get_object_or_404(AIKnowledgeItem, id=item_id)
            item.delete()
            messages.success(request, "Knowledge item deleted.")
            return redirect('ai_assistant:cms_knowledge_base')

    return render(request, 'ai_assistant/knowledge_base.html', {'knowledge_items': items})
