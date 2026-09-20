from django import template
from django.utils import timezone
from django.db.models import Sum
from crm.models import Lead, FollowUp, SiteVisit, Estimate, LeadActivity
from blog.models import BlogPost, BlogCategory
from projects.models import Project, SupportTicket
from core.models import Testimonial, FAQ
from services.models import Service, ServiceCategory
from payments.models import PaymentTransaction, PaymentRequest
from ai_assistant.models import ChatSession

register = template.Library()

@register.simple_tag
def get_admin_metrics():
    today = timezone.now().date()
    
    # 1. CRM Metrics
    total_leads = Lead.objects.filter(is_deleted=False).count()
    new_leads = Lead.objects.filter(status='NEW', is_deleted=False).count()
    site_visits_pending = SiteVisit.objects.filter(status='SCHEDULED').count()
    site_visits_today = SiteVisit.objects.filter(visit_date=today, status='SCHEDULED').count()
    won_leads = Lead.objects.filter(status='WON', is_deleted=False).count()
    open_proposals = Estimate.objects.filter(status__in=['sent', 'under_discussion']).count()
    
    followups_today = FollowUp.objects.filter(
        follow_up_date=today,
        completed=False
    ).count()

    # 2. Payments & Finance Metrics
    total_revenue = PaymentTransaction.objects.filter(status='SUCCESS').aggregate(total=Sum('amount'))['total'] or 0
    successful_tx_count = PaymentTransaction.objects.filter(status='SUCCESS').count()
    pending_payment_requests = PaymentRequest.objects.filter(status='PENDING').count()
    pending_verification_count = PaymentTransaction.objects.filter(status='MANUAL_REVIEW').count()

    # 3. AI Assistant Metrics
    total_ai_sessions = ChatSession.objects.count()
    ai_leads_count = Lead.objects.filter(lead_source_text__icontains='AI', is_deleted=False).count()
    active_handoffs = ChatSession.objects.filter(status__in=['human_handoff', 'human_active']).count()

    # 4. CMS & Content Metrics
    published_blogs = BlogPost.objects.filter(status='published').count()
    total_projects = Project.objects.filter(published=True).count()
    total_services = Service.objects.filter(published=True).count()
    total_categories = ServiceCategory.objects.count()
    total_testimonials = Testimonial.objects.count()
    total_faqs = FAQ.objects.count()
    open_support_tickets = SupportTicket.objects.filter(status__in=['OPEN', 'IN_PROGRESS']).count()

    # 5. Streams
    recent_leads = Lead.objects.filter(is_deleted=False).select_related('assigned_to', 'lead_source').order_by('-created_at')[:6]
    recent_projects = Project.objects.filter(published=True).select_related('category').order_by('-created_at')[:4]
    recent_transactions = PaymentTransaction.objects.select_related('payment_request').order_by('-created_at')[:5]
    recent_activities = LeadActivity.objects.select_related('lead', 'performed_by').order_by('-created_at')[:8]

    return {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'site_visits_pending': site_visits_pending,
        'site_visits_today': site_visits_today,
        'won_leads': won_leads,
        'open_proposals': open_proposals,
        'pending_proposals': open_proposals,
        'followups_today': followups_today,
        'total_revenue': total_revenue,
        'successful_tx_count': successful_tx_count,
        'pending_payment_requests': pending_payment_requests,
        'pending_verification_count': pending_verification_count,
        'total_ai_sessions': total_ai_sessions,
        'ai_chat_sessions': total_ai_sessions,
        'ai_leads_count': ai_leads_count,
        'ai_leads_converted': ai_leads_count,
        'active_handoffs': active_handoffs,
        'published_blogs': published_blogs,
        'total_projects': total_projects,
        'active_projects': total_projects,
        'total_services': total_services,
        'total_categories': total_categories,
        'total_testimonials': total_testimonials,
        'total_faqs': total_faqs,
        'open_support_tickets': open_support_tickets,
        'recent_leads': recent_leads,
        'recent_projects': recent_projects,
        'recent_transactions': recent_transactions,
        'recent_activities': recent_activities,
    }
