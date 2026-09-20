from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from .models import Lead, LeadSource, FollowUp, SiteVisit, Estimate, LeadNote, LeadActivity
from .forms import (
    LeadForm, LeadQuickAssignForm, LeadMarkWonForm, LeadMarkLostForm,
    LeadOnHoldForm, FollowUpForm, SiteVisitForm, EstimateForm, LeadNoteForm, LeadSourceForm
)

def staff_required(view_func):
    """Decorator ensuring only active staff members can access CRM."""
    return login_required(user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='/cms/login/')(view_func))


def log_activity(lead, activity_type, title, description="", user=None):
    """Utility to record chronological CRM audit log entries."""
    return LeadActivity.objects.create(
        lead=lead,
        activity_type=activity_type,
        title=title,
        description=description,
        performed_by=user if user and user.is_authenticated else None
    )


def get_crm_queryset(user, include_deleted=False):
    """Return accessible leads based on user role and soft-delete state."""
    qs = Lead.objects.all() if include_deleted else Lead.objects.filter(is_deleted=False)
    
    # Non-superusers / sales staff can view leads assigned to them or unassigned
    if not (user.is_superuser or user.groups.filter(name__in=['Admin', 'Manager']).exists()):
        qs = qs.filter(Q(assigned_to=user) | Q(assigned_to__isnull=True))
    
    return qs


# ==============================================================================
# 1. CRM DASHBOARD & KPI METRICS
# ==============================================================================
@staff_required
def crm_dashboard(request):
    """Main CRM Executive Dashboard with Real-Time Funnel Metrics."""
    user = request.user
    leads_qs = get_crm_queryset(user)

    # Date Range Filtering
    date_filter = request.GET.get('range', 'this_month')
    now = timezone.now()
    today = now.date()

    if date_filter == 'today':
        leads_qs = leads_qs.filter(created_at__date=today)
    elif date_filter == 'yesterday':
        leads_qs = leads_qs.filter(created_at__date=today - timedelta(days=1))
    elif date_filter == 'last_7_days':
        leads_qs = leads_qs.filter(created_at__gte=now - timedelta(days=7))
    elif date_filter == 'last_30_days':
        leads_qs = leads_qs.filter(created_at__gte=now - timedelta(days=30))
    elif date_filter == 'this_month':
        leads_qs = leads_qs.filter(created_at__year=now.year, created_at__month=now.month)
    elif date_filter == 'last_month':
        first_day_this_month = today.replace(day=1)
        last_day_prev_month = first_day_this_month - timedelta(days=1)
        leads_qs = leads_qs.filter(created_at__year=last_day_prev_month.year, created_at__month=last_day_prev_month.month)
    elif date_filter == 'custom':
        start = request.GET.get('start_date')
        end = request.GET.get('end_date')
        if start:
            leads_qs = leads_qs.filter(created_at__date__gte=start)
        if end:
            leads_qs = leads_qs.filter(created_at__date__lte=end)

    # Aggregated KPI Summary
    total_leads = leads_qs.count()
    new_leads = leads_qs.filter(status='NEW').count()
    won_leads = leads_qs.filter(status='WON').count()
    lost_leads = leads_qs.filter(status='LOST').count()
    on_hold_leads = leads_qs.filter(status='ON_HOLD').count()

    # Active Pipeline & Won Value
    pipeline_val = leads_qs.exclude(status__in=['WON', 'LOST']).aggregate(val=Sum('expected_project_value'))['val'] or 0
    won_val = leads_qs.filter(status='WON').aggregate(val=Sum('final_project_value'))['val'] or 0
    if won_val == 0:
        won_val = leads_qs.filter(status='WON').aggregate(val=Sum('expected_project_value'))['val'] or 0

    # Follow-ups and Site visits (global or user-specific)
    fu_qs = FollowUp.objects.filter(lead__is_deleted=False)
    if not (user.is_superuser or user.groups.filter(name__in=['Admin', 'Manager']).exists()):
        fu_qs = fu_qs.filter(Q(assigned_to=user) | Q(lead__assigned_to=user))

    today_followups = fu_qs.filter(follow_up_date=today, completed=False).count()
    overdue_followups = fu_qs.filter(follow_up_date__lt=today, completed=False).count()

    sv_qs = SiteVisit.objects.filter(lead__is_deleted=False)
    today_site_visits = sv_qs.filter(visit_date=today, status='scheduled').count()
    upcoming_site_visits = sv_qs.filter(visit_date__gte=today, status='scheduled').count()

    # Visual Funnel Stage Counts
    stages = [
        {'code': 'NEW', 'label': 'NEW', 'count': leads_qs.filter(status='NEW').count(), 'badge': 'bg-primary'},
        {'code': 'CONTACTED', 'label': 'CONTACTED', 'count': leads_qs.filter(status='CONTACTED').count(), 'badge': 'bg-info text-dark'},
        {'code': 'QUALIFIED', 'label': 'QUALIFIED', 'count': leads_qs.filter(status='QUALIFIED').count(), 'badge': 'bg-secondary'},
        {'code': 'SITE_VISIT', 'label': 'SITE VISIT', 'count': leads_qs.filter(status='SITE_VISIT').count(), 'badge': 'bg-warning text-dark'},
        {'code': 'REQUIREMENT_CONFIRMED', 'label': 'REQ. CONFIRMED', 'count': leads_qs.filter(status='REQUIREMENT_CONFIRMED').count(), 'badge': 'bg-primary'},
        {'code': 'ESTIMATE_PREPARED', 'label': 'ESTIMATE', 'count': leads_qs.filter(status='ESTIMATE_PREPARED').count(), 'badge': 'bg-info text-dark'},
        {'code': 'PROPOSAL_SENT', 'label': 'PROPOSAL', 'count': leads_qs.filter(status='PROPOSAL_SENT').count(), 'badge': 'bg-indigo text-white'},
        {'code': 'NEGOTIATION', 'label': 'NEGOTIATION', 'count': leads_qs.filter(status='NEGOTIATION').count(), 'badge': 'bg-dark text-white'},
        {'code': 'WON', 'label': 'WON', 'count': won_leads, 'badge': 'bg-success'},
        {'code': 'LOST', 'label': 'LOST', 'count': lost_leads, 'badge': 'bg-danger'},
        {'code': 'ON_HOLD', 'label': 'ON HOLD', 'count': on_hold_leads, 'badge': 'bg-light text-dark border'},
    ]

    recent_leads = leads_qs.select_related('assigned_to', 'lead_source')[:10]
    upcoming_fu_list = fu_qs.filter(follow_up_date__gte=today, completed=False).select_related('lead', 'assigned_to')[:6]

    context = {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'won_leads': won_leads,
        'lost_leads': lost_leads,
        'on_hold_leads': on_hold_leads,
        'pipeline_value': pipeline_val,
        'won_value': won_val,
        'today_followups': today_followups,
        'overdue_followups': overdue_followups,
        'today_site_visits': today_site_visits,
        'upcoming_site_visits': upcoming_site_visits,
        'stages': stages,
        'recent_leads': recent_leads,
        'upcoming_fu_list': upcoming_fu_list,
        'date_filter': date_filter,
    }
    return render(request, 'crm/dashboard.html', context)


# ==============================================================================
# 2. LEAD LIST, SEARCH & ADVANCED FILTERS
# ==============================================================================
@staff_required
def crm_lead_list(request):
    """Lead Directory with multi-field search, filters, soft delete trash & pagination."""
    user = request.user
    view_tab = request.GET.get('view', 'active')  # 'active' or 'trash'
    
    if view_tab == 'trash' and (user.is_superuser or user.is_staff):
        leads = get_crm_queryset(user, include_deleted=True).filter(is_deleted=True)
    else:
        leads = get_crm_queryset(user, include_deleted=False)

    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        leads = leads.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query) |
            Q(lead_id__icontains=query) |
            Q(city__icontains=query) |
            Q(property_location__icontains=query) |
            Q(company_name__icontains=query) |
            Q(project_description__icontains=query)
        )

    # Filters
    cat_filter = request.GET.get('category', '')
    if cat_filter:
        leads = leads.filter(service_category=cat_filter)

    type_filter = request.GET.get('service_type', '')
    if type_filter:
        leads = leads.filter(service_type=type_filter)

    status_filter = request.GET.get('status', '')
    if status_filter:
        leads = leads.filter(status=status_filter)

    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        leads = leads.filter(priority=priority_filter)

    assigned_filter = request.GET.get('assigned_to', '')
    if assigned_filter:
        if assigned_filter == 'unassigned':
            leads = leads.filter(assigned_to__isnull=True)
        else:
            leads = leads.filter(assigned_to_id=assigned_filter)

    source_filter = request.GET.get('source', '')
    if source_filter:
        leads = leads.filter(lead_source_id=source_filter)

    customer_filter = request.GET.get('customer_type', '')
    if customer_filter:
        leads = leads.filter(customer_type=customer_filter)

    prop_filter = request.GET.get('property_type', '')
    if prop_filter:
        leads = leads.filter(property_type=prop_filter)

    # Pagination (15 leads per page)
    paginator = Paginator(leads.select_related('assigned_to', 'lead_source'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'leads': page_obj,
        'total_count': leads.count(),
        'view_tab': view_tab,
        'query': query,
        'category_filter': cat_filter,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'assigned_filter': assigned_filter,
        'source_filter': source_filter,
        'customer_filter': customer_filter,
        'prop_filter': prop_filter,
        'service_categories': Lead.SERVICE_CATEGORIES,
        'service_types': Lead.SERVICE_TYPES,
        'status_choices': Lead.STATUS_CHOICES,
        'priority_choices': Lead.PRIORITY_CHOICES,
        'customer_types': Lead.CUSTOMER_TYPES,
        'property_types': Lead.PROPERTY_TYPES,
        'sources': LeadSource.objects.filter(is_active=True),
        'staff_users': User.objects.filter(is_staff=True),
    }
    return render(request, 'crm/lead_list.html', context)


# ==============================================================================
# 3. CREATE LEAD
# ==============================================================================
@staff_required
def crm_lead_create(request):
    """Add a new CRM Lead manually."""
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.save()
            log_activity(lead, 'created', 'Lead Created', f"Lead created manually by {request.user.get_full_name() or request.user.username}", request.user)
            
            messages.success(request, f"Lead [{lead.lead_id}] for '{lead.full_name}' created successfully.")
            
            if 'save_and_schedule' in request.POST:
                return redirect(f"/cms/crm/leads/{lead.pk}/?tab=followup&action=add")
            return redirect('crm:lead_detail', pk=lead.pk)
    else:
        initial = {'assigned_to': request.user}
        form = LeadForm(initial=initial)

    return render(request, 'crm/lead_create.html', {'form': form})


# ==============================================================================
# 4. LEAD DETAIL & 360-DEGREE PROFILE
# ==============================================================================
@staff_required
def crm_lead_detail(request, pk):
    """Comprehensive 360-Degree CRM Lead Profile & Action Desk."""
    lead = get_object_or_404(Lead, pk=pk)

    # Permission check for sales staff
    if not (request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Manager']).exists()):
        if lead.assigned_to and lead.assigned_to != request.user:
            messages.warning(request, "You only have restricted access to your assigned leads.")

    # Timeline, Follow-ups, Site visits, Estimates, Notes
    activities = lead.activities.all().select_related('performed_by')[:20]
    follow_ups = lead.follow_ups.all().select_related('assigned_to')
    site_visits = lead.site_visits.all().select_related('assigned_staff')
    estimates = lead.estimates.all()
    notes = lead.notes.all().select_related('created_by')

    # Quick action modal forms
    assign_form = LeadQuickAssignForm(instance=lead)
    mark_won_form = LeadMarkWonForm(instance=lead)
    mark_lost_form = LeadMarkLostForm(instance=lead)
    on_hold_form = LeadOnHoldForm(instance=lead)
    followup_form = FollowUpForm(initial={'assigned_to': request.user, 'follow_up_date': timezone.now().date()})
    sitevisit_form = SiteVisitForm(initial={'assigned_staff': request.user, 'visit_date': timezone.now().date(), 'site_address': lead.property_location or lead.city})
    estimate_form = EstimateForm(initial={'estimate_date': timezone.now().date()})
    note_form = LeadNoteForm()

    context = {
        'lead': lead,
        'activities': activities,
        'follow_ups': follow_ups,
        'site_visits': site_visits,
        'estimates': estimates,
        'notes': notes,
        'assign_form': assign_form,
        'mark_won_form': mark_won_form,
        'mark_lost_form': mark_lost_form,
        'on_hold_form': on_hold_form,
        'followup_form': followup_form,
        'sitevisit_form': sitevisit_form,
        'estimate_form': estimate_form,
        'note_form': note_form,
        'active_tab': request.GET.get('tab', 'timeline'),
    }
    return render(request, 'crm/lead_detail.html', context)


# ==============================================================================
# 5. EDIT LEAD
# ==============================================================================
@staff_required
def crm_lead_edit(request, pk):
    """Edit an existing Lead."""
    lead = get_object_or_404(Lead, pk=pk)
    old_status = lead.status
    old_assigned = lead.assigned_to

    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            updated_lead = form.save()

            # Log audit trail if status changed
            if updated_lead.status != old_status:
                log_activity(updated_lead, 'status_changed', f"Status changed to {updated_lead.get_status_display()}", f"Updated from {dict(Lead.STATUS_CHOICES).get(old_status)} by {request.user.username}", request.user)

            # Log audit trail if staff assignment changed
            if updated_lead.assigned_to != old_assigned:
                assigned_name = updated_lead.assigned_to.get_full_name() or updated_lead.assigned_to.username if updated_lead.assigned_to else "Unassigned"
                log_activity(updated_lead, 'assigned', f"Lead Assigned to {assigned_name}", f"Assigned by {request.user.username}", request.user)

            messages.success(request, f"Lead [{lead.lead_id}] updated successfully.")
            return redirect('crm:lead_detail', pk=lead.pk)
    else:
        form = LeadForm(instance=lead)

    return render(request, 'crm/lead_edit.html', {'form': form, 'lead': lead})


# ==============================================================================
# 6. SOFT DELETE, RESTORE & PERMANENT DELETE
# ==============================================================================
@staff_required
def crm_lead_delete(request, pk):
    """Soft delete confirmation & execution."""
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        lead.is_deleted = True
        lead.deleted_at = timezone.now()
        lead.deleted_by = request.user
        lead.save()
        log_activity(lead, 'status_changed', 'Lead Soft-Deleted', f"Moved to trash by {request.user.username}", request.user)
        messages.info(request, f"Lead [{lead.lead_id}] for '{lead.full_name}' moved to Trash.")
        return redirect('crm:lead_list')

    return render(request, 'crm/lead_delete.html', {'lead': lead})


@staff_required
@require_POST
def crm_lead_restore(request, pk):
    """Restore a soft-deleted lead from trash."""
    lead = get_object_or_404(Lead, pk=pk, is_deleted=True)
    lead.is_deleted = False
    lead.deleted_at = None
    lead.deleted_by = None
    lead.save()
    log_activity(lead, 'restored', 'Lead Restored from Trash', f"Restored by {request.user.username}", request.user)
    messages.success(request, f"Lead [{lead.lead_id}] restored successfully.")
    return redirect('crm:lead_detail', pk=lead.pk)


@staff_required
@require_POST
def crm_lead_permanent_delete(request, pk):
    """Permanent database removal of a lead (Admin only)."""
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
        messages.error(request, "Permanent deletion requires Administrator permissions.")
        return redirect('crm:lead_list')

    lead = get_object_or_404(Lead, pk=pk, is_deleted=True)
    lead_id_str = lead.lead_id
    lead.delete()
    messages.success(request, f"Lead [{lead_id_str}] permanently deleted from database.")
    return redirect('/cms/crm/leads/?view=trash')


# ==============================================================================
# 7. WORKFLOW ACTIONS (ASSIGN, WON, LOST, ON HOLD, NOTES)
# ==============================================================================
@staff_required
@require_POST
def crm_lead_assign(request, pk):
    """Assign lead to staff member."""
    lead = get_object_or_404(Lead, pk=pk)
    form = LeadQuickAssignForm(request.POST, instance=lead)
    if form.is_valid():
        updated = form.save()
        staff_str = updated.assigned_to.get_full_name() or updated.assigned_to.username if updated.assigned_to else "Unassigned"
        log_activity(lead, 'assigned', f"Assigned to {staff_str}", f"Priority: {updated.get_priority_display()}", request.user)
        messages.success(request, f"Lead assigned to {staff_str}.")
    return redirect('crm:lead_detail', pk=lead.pk)


@staff_required
@require_POST
def crm_lead_mark_won(request, pk):
    """Mark lead as Won with closing project value."""
    lead = get_object_or_404(Lead, pk=pk)
    form = LeadMarkWonForm(request.POST, instance=lead)
    if form.is_valid():
        lead = form.save(commit=False)
        lead.status = 'WON'
        if not lead.won_date:
            lead.won_date = timezone.now().date()
        lead.save()

        won_notes = form.cleaned_data.get('won_notes')
        desc = f"Won Project Value: ₹{lead.final_project_value:,.2f}"
        if won_notes:
            desc += f"\nNotes: {won_notes}"
            LeadNote.objects.create(lead=lead, note=f"[PROJECT WON]: {won_notes}", created_by=request.user)

        log_activity(lead, 'marked_won', 'Project WON! 🏆', desc, request.user)
        messages.success(request, f"🎉 Congratulations! Lead [{lead.lead_id}] marked as WON for ₹{lead.final_project_value:,.2f}!")
    return redirect('crm:lead_detail', pk=lead.pk)


@staff_required
@require_POST
def crm_lead_mark_lost(request, pk):
    """Mark lead as Lost with mandatory reason."""
    lead = get_object_or_404(Lead, pk=pk)
    form = LeadMarkLostForm(request.POST, instance=lead)
    if form.is_valid():
        lead = form.save(commit=False)
        lead.status = 'LOST'
        lead.save()

        desc = f"Lost Reason: {lead.get_lost_reason_display()}"
        if lead.lost_notes:
            desc += f"\nNotes: {lead.lost_notes}"

        log_activity(lead, 'marked_lost', 'Lead Marked Lost', desc, request.user)
        messages.info(request, f"Lead [{lead.lead_id}] marked as LOST ({lead.get_lost_reason_display()}).")
    return redirect('crm:lead_detail', pk=lead.pk)


@staff_required
@require_POST
def crm_lead_on_hold(request, pk):
    """Place lead on hold with future scheduled resumption."""
    lead = get_object_or_404(Lead, pk=pk)
    form = LeadOnHoldForm(request.POST, instance=lead)
    if form.is_valid():
        lead = form.save(commit=False)
        lead.status = 'ON_HOLD'
        lead.save()

        desc = f"Reason: {lead.on_hold_reason}"
        if lead.next_follow_up_date:
            desc += f"\nResumption Follow-up: {lead.next_follow_up_date.strftime('%d %b %Y, %I:%M %p')}"

        log_activity(lead, 'status_changed', 'Lead Placed On Hold ⏸', desc, request.user)
        messages.info(request, f"Lead [{lead.lead_id}] placed ON HOLD.")
    return redirect('crm:lead_detail', pk=lead.pk)


@staff_required
@require_POST
def crm_lead_note_create(request, pk):
    """Add a quick discussion note to a lead."""
    lead = get_object_or_404(Lead, pk=pk)
    form = LeadNoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.lead = lead
        note.created_by = request.user
        note.save()
        log_activity(lead, 'note_added', 'Note Added', note.note[:150], request.user)
        messages.success(request, "Internal note recorded.")
    return redirect(f"/cms/crm/leads/{lead.pk}/?tab=notes")


# ==============================================================================
# 8. FOLLOW-UPS MODULE
# ==============================================================================
@staff_required
def crm_followup_list(request):
    """Follow-up Communication Management Center."""
    user = request.user
    today = timezone.now().date()

    fu_qs = FollowUp.objects.filter(lead__is_deleted=False).select_related('lead', 'assigned_to')
    if not (user.is_superuser or user.groups.filter(name__in=['Admin', 'Manager']).exists()):
        fu_qs = fu_qs.filter(Q(assigned_to=user) | Q(lead__assigned_to=user))

    tab = request.GET.get('tab', 'today')
    if tab == 'today':
        followups = fu_qs.filter(follow_up_date=today, completed=False)
    elif tab == 'upcoming':
        followups = fu_qs.filter(follow_up_date__gt=today, completed=False)
    elif tab == 'overdue':
        followups = fu_qs.filter(follow_up_date__lt=today, completed=False)
    elif tab == 'completed':
        followups = fu_qs.filter(completed=True)
    else:
        followups = fu_qs.filter(completed=False)

    context = {
        'followups': followups,
        'tab': tab,
        'today_count': fu_qs.filter(follow_up_date=today, completed=False).count(),
        'upcoming_count': fu_qs.filter(follow_up_date__gt=today, completed=False).count(),
        'overdue_count': fu_qs.filter(follow_up_date__lt=today, completed=False).count(),
        'completed_count': fu_qs.filter(completed=True).count(),
    }
    return render(request, 'crm/followup_list.html', context)


@staff_required
@require_POST
def crm_followup_create(request, lead_pk):
    """Schedule / Log a follow-up for a lead."""
    lead = get_object_or_404(Lead, pk=lead_pk)
    form = FollowUpForm(request.POST)
    if form.is_valid():
        fu = form.save(commit=False)
        fu.lead = lead
        if not fu.assigned_to:
            fu.assigned_to = request.user
        if fu.completed and not fu.completed_at:
            fu.completed_at = timezone.now()
        fu.save()

        # Update lead's next follow up date
        if fu.next_follow_up_date:
            lead.next_follow_up_date = fu.next_follow_up_date
            lead.save(update_fields=['next_follow_up_date'])

        log_activity(lead, 'followup_added', f"Follow-up Scheduled ({fu.get_follow_up_type_display()})", f"Subject: {fu.subject}\nDate: {fu.follow_up_date}", request.user)
        messages.success(request, f"Follow-up scheduled for {fu.follow_up_date}.")
    return redirect(f"/cms/crm/leads/{lead.pk}/?tab=followup")


@staff_required
@require_POST
def crm_followup_complete(request, pk):
    """Mark a follow-up as completed with outcome."""
    fu = get_object_or_404(FollowUp, pk=pk)
    outcome = request.POST.get('outcome', '').strip()
    next_date = request.POST.get('next_follow_up_date')

    fu.completed = True
    fu.completed_at = timezone.now()
    if outcome:
        fu.outcome = outcome
    fu.save()

    log_activity(fu.lead, 'followup_completed', f"Follow-up Completed ({fu.get_follow_up_type_display()})", f"Outcome: {outcome or 'Completed'}", request.user)

    if next_date:
        fu.lead.next_follow_up_date = next_date
        fu.lead.save(update_fields=['next_follow_up_date'])

    messages.success(request, "Follow-up marked as completed.")
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/cms/crm/follow-ups/'
    return redirect(next_url)


# ==============================================================================
# 9. SITE VISITS MODULE
# ==============================================================================
@staff_required
def crm_sitevisit_list(request):
    """Site Visits & Inspection Calendar."""
    user = request.user
    today = timezone.now().date()

    sv_qs = SiteVisit.objects.filter(lead__is_deleted=False).select_related('lead', 'assigned_staff')
    if not (user.is_superuser or user.groups.filter(name__in=['Admin', 'Manager', 'Site Engineer']).exists()):
        sv_qs = sv_qs.filter(Q(assigned_staff=user) | Q(lead__assigned_to=user))

    status_filter = request.GET.get('status', 'scheduled')
    if status_filter:
        site_visits = sv_qs.filter(status=status_filter)
    else:
        site_visits = sv_qs

    context = {
        'site_visits': site_visits,
        'status_filter': status_filter,
        'today_count': sv_qs.filter(visit_date=today, status='scheduled').count(),
        'upcoming_count': sv_qs.filter(visit_date__gte=today, status='scheduled').count(),
        'completed_count': sv_qs.filter(status='completed').count(),
    }
    return render(request, 'crm/sitevisit_list.html', context)


@staff_required
@require_POST
def crm_sitevisit_create(request, lead_pk):
    """Schedule on-site technical inspection."""
    lead = get_object_or_404(Lead, pk=lead_pk)
    form = SiteVisitForm(request.POST)
    if form.is_valid():
        sv = form.save(commit=False)
        sv.lead = lead
        if not sv.assigned_staff:
            sv.assigned_staff = request.user
        sv.save()

        # Update lead stage if appropriate
        if lead.status in ['NEW', 'CONTACTED', 'QUALIFIED']:
            lead.status = 'SITE_VISIT'
            lead.save(update_fields=['status'])

        log_activity(lead, 'sitevisit_scheduled', f"Site Visit Scheduled for {sv.visit_date}", f"Address: {sv.site_address}\nAssigned Engineer: {sv.assigned_staff.get_full_name() or sv.assigned_staff.username}", request.user)
        messages.success(request, f"Site visit scheduled for {sv.visit_date}.")
    return redirect(f"/cms/crm/leads/{lead.pk}/?tab=sitevisit")


# ==============================================================================
# 10. ESTIMATES & PROPOSALS MODULE
# ==============================================================================
@staff_required
def crm_estimate_list(request):
    """Estimate & Proposal Tracking Desk."""
    estimates = Estimate.objects.filter(lead__is_deleted=False).select_related('lead')
    status_filter = request.GET.get('status', '')
    if status_filter:
        estimates = estimates.filter(status=status_filter)

    total_value = estimates.aggregate(val=Sum('total_amount'))['val'] or 0

    context = {
        'estimates': estimates,
        'status_filter': status_filter,
        'total_value': total_value,
        'statuses': Estimate.ESTIMATE_STATUSES,
    }
    return render(request, 'crm/estimate_list.html', context)


@staff_required
@require_POST
def crm_estimate_create(request, lead_pk):
    """Create and link a BOQ Estimate / Proposal to a lead."""
    lead = get_object_or_404(Lead, pk=lead_pk)
    form = EstimateForm(request.POST)
    if form.is_valid():
        est = form.save(commit=False)
        est.lead = lead
        est.save()

        # Update lead expected project value and stage
        lead.expected_project_value = est.total_amount
        if lead.status in ['NEW', 'CONTACTED', 'QUALIFIED', 'SITE_VISIT', 'REQUIREMENT_CONFIRMED']:
            lead.status = 'ESTIMATE_PREPARED'
        lead.save()

        log_activity(lead, 'estimate_created', f"Estimate Added ({est.estimate_number})", f"Amount: ₹{est.total_amount:,.2f}\nStatus: {est.get_status_display()}", request.user)
        messages.success(request, f"Estimate {est.estimate_number} (₹{est.total_amount:,.2f}) added.")
    return redirect(f"/cms/crm/leads/{lead.pk}/?tab=estimates")


# ==============================================================================
# 11. CRM CONVERSION REPORTS & ANALYTICS
# ==============================================================================
@staff_required
def crm_reports(request):
    """Executive CRM Conversion Analytics & Service Breakdowns."""
    leads = Lead.objects.filter(is_deleted=False)

    total_leads = leads.count() or 1  # prevent div by zero

    # Conversion Funnel Metrics
    qualified_count = leads.exclude(status__in=['NEW', 'CONTACTED']).count()
    site_visit_count = leads.filter(Q(status__in=['SITE_VISIT', 'REQUIREMENT_CONFIRMED', 'ESTIMATE_PREPARED', 'PROPOSAL_SENT', 'NEGOTIATION', 'WON']) | Q(site_visits__isnull=False)).distinct().count()
    proposal_count = leads.filter(Q(status__in=['ESTIMATE_PREPARED', 'PROPOSAL_SENT', 'NEGOTIATION', 'WON']) | Q(estimates__isnull=False)).distinct().count()
    won_count = leads.filter(status='WON').count()
    lost_count = leads.filter(status='LOST').count()

    conv_metrics = {
        'qualified_rate': round((qualified_count / total_leads) * 100, 1),
        'site_visit_rate': round((site_visit_count / total_leads) * 100, 1),
        'proposal_rate': round((proposal_count / total_leads) * 100, 1),
        'won_rate': round((won_count / total_leads) * 100, 1),
        'lost_rate': round((lost_count / total_leads) * 100, 1),
    }

    # Service Distribution Report
    service_report = leads.values('service_category').annotate(
        count=Count('id'),
        won_count=Count('id', filter=Q(status='WON')),
        pipeline_val=Sum('expected_project_value'),
        won_val=Sum('final_project_value')
    ).order_by('-count')

    # Source Performance Report
    source_report = leads.values('lead_source__name', 'lead_source_text').annotate(
        count=Count('id'),
        won_count=Count('id', filter=Q(status='WON')),
        won_val=Sum('final_project_value')
    ).order_by('-count')

    # Sales Staff Performance
    staff_report = User.objects.filter(is_staff=True).annotate(
        assigned_leads=Count('assigned_crm_leads', filter=Q(assigned_crm_leads__is_deleted=False)),
        won_leads=Count('assigned_crm_leads', filter=Q(assigned_crm_leads__is_deleted=False, assigned_crm_leads__status='WON')),
        lost_leads=Count('assigned_crm_leads', filter=Q(assigned_crm_leads__is_deleted=False, assigned_crm_leads__status='LOST')),
        won_val=Sum('assigned_crm_leads__final_project_value', filter=Q(assigned_crm_leads__is_deleted=False, assigned_crm_leads__status='WON')),
        pipeline_val=Sum('assigned_crm_leads__expected_project_value', filter=Q(assigned_crm_leads__is_deleted=False) & ~Q(assigned_crm_leads__status__in=['WON', 'LOST']))
    ).order_by('-assigned_leads')

    context = {
        'total_leads': total_leads,
        'won_count': won_count,
        'lost_count': lost_count,
        'conv_metrics': conv_metrics,
        'service_report': service_report,
        'source_report': source_report,
        'staff_report': staff_report,
        'service_dict': dict(Lead.SERVICE_CATEGORIES),
    }
    return render(request, 'crm/reports.html', context)


# ==============================================================================
# 12. CRM SETTINGS & LEAD SOURCES
# ==============================================================================
@staff_required
def crm_settings(request):
    """Manage Lead Sources & CRM Configurations."""
    sources = LeadSource.objects.all().annotate(lead_count=Count('leads'))

    if request.method == 'POST':
        form = LeadSourceForm(request.POST)
        if form.is_valid():
            src = form.save()
            messages.success(request, f"Lead Source '{src.name}' added successfully.")
            return redirect('crm:settings')
    else:
        form = LeadSourceForm()

    return render(request, 'crm/settings.html', {'sources': sources, 'form': form})
