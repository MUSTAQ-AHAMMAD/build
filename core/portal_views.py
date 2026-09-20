from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone

from projects.models import Project, ProjectTask, ProjectDocument, SupportTicket, SupportTicketMessage
from crm.models import Lead, SiteVisit, Estimate
from payments.models import PaymentRequest, PaymentTransaction, PaymentReceipt, PaymentSettings
from core.models import WebsiteSettings

def portal_register(request):
    """Customer self-registration portal"""
    if request.user.is_authenticated:
        return redirect('core:portal_dashboard')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')

        if not email or not password or not full_name:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'portal/register.html')

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email address already exists. Please log in.")
            return redirect('core:portal_login')

        name_parts = full_name.split(' ', 1)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name_parts[0],
            last_name=name_parts[1] if len(name_parts) > 1 else ''
        )

        # Connect user with existing CRM Leads or Projects by phone / email
        Lead.objects.filter(Q(email__iexact=email) | Q(phone=phone)).update(assigned_to=user)
        Project.objects.filter(Q(customer_email__iexact=email) | Q(customer_phone=phone)).update(customer_user=user)

        login(request, user)
        messages.success(request, f"Welcome to BUILD+ Client Portal, {user.first_name}!")
        return redirect('core:portal_dashboard')

    return render(request, 'portal/register.html')


def portal_login(request):
    """Customer Portal login"""
    if request.user.is_authenticated:
        return redirect('core:portal_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if not user:
            # Try by email lookup
            user_by_email = User.objects.filter(email__iexact=username).first()
            if user_by_email:
                user = authenticate(request, username=user_by_email.username, password=password)

        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('core:portal_dashboard')
        else:
            messages.error(request, "Invalid email address or password.")

    return render(request, 'portal/login.html')


def portal_logout(request):
    """Customer Portal logout"""
    logout(request)
    messages.info(request, "You have been logged out of the Client Portal.")
    return redirect('core:home')


@login_required(login_url='/portal/login/')
def portal_dashboard(request):
    """Customer Portal Executive Overview"""
    user = request.user
    user_email = user.email or user.username

    # Fetch Customer's Projects
    projects = Project.objects.filter(
        Q(customer_user=user) | Q(customer_email__iexact=user_email)
    ).distinct()

    # Fetch Customer's Site Inspections
    site_visits = SiteVisit.objects.filter(
        Q(lead__email__iexact=user_email) | Q(lead__phone=user.username)
    ).distinct()

    # Fetch Customer's Estimates & Proposals
    estimates = Estimate.objects.filter(
        Q(lead__email__iexact=user_email) | Q(lead__phone=user.username)
    ).distinct()
    proposals = estimates.filter(status__in=['sent', 'under_discussion', 'approved', 'rejected'])

    # Fetch Payments & Invoices
    payment_requests = PaymentRequest.objects.filter(
        Q(customer_email__iexact=user_email) | Q(lead__email__iexact=user_email)
    ).distinct()
    transactions = PaymentTransaction.objects.filter(
        Q(customer_email__iexact=user_email) | Q(lead__email__iexact=user_email)
    ).distinct()

    # Fetch Open Support Tickets
    tickets = SupportTicket.objects.filter(
        Q(customer_user=user) | Q(customer_email__iexact=user_email)
    ).distinct()

    context = {
        'projects': projects,
        'site_visits': site_visits,
        'estimates': estimates,
        'proposals': proposals,
        'payment_requests': payment_requests,
        'transactions': transactions,
        'tickets': tickets,
        'settings': WebsiteSettings.load(),
        'pay_settings': PaymentSettings.load(),
    }
    return render(request, 'portal/dashboard.html', context)


@login_required(login_url='/portal/login/')
def portal_projects(request):
    """Customer Portal Projects directory"""
    user_email = request.user.email or request.user.username
    projects = Project.objects.filter(
        Q(customer_user=request.user) | Q(customer_email__iexact=user_email)
    ).distinct()

    return render(request, 'portal/projects.html', {'projects': projects})


@login_required(login_url='/portal/login/')
def portal_project_detail(request, slug):
    """Customer Portal 360° Project Execution & Milestone Tracker"""
    project = get_object_or_404(Project, slug=slug)
    
    # Milestone progress
    milestones = project.payment_milestones.all()
    tasks = project.tasks.all()
    documents = project.documents.filter(visibility__in=['CUSTOMER', 'PUBLIC'])

    context = {
        'project': project,
        'milestones': milestones,
        'tasks': tasks,
        'documents': documents,
        'pay_settings': PaymentSettings.load(),
    }
    return render(request, 'portal/project_detail.html', context)


@login_required(login_url='/portal/login/')
def portal_estimates(request):
    """Customer Portal Estimates & Line-by-Line BOQ Breakdown"""
    user_email = request.user.email or request.user.username
    estimates = Estimate.objects.filter(
        Q(lead__email__iexact=user_email) | Q(lead__phone=request.user.username)
    ).distinct()

    return render(request, 'portal/estimates.html', {'estimates': estimates, 'pay_settings': PaymentSettings.load()})


@login_required(login_url='/portal/login/')
def portal_proposals(request):
    """Customer Portal Commercial Proposals & Agreement Acceptance"""
    user_email = request.user.email or request.user.username
    proposals = Estimate.objects.filter(
        Q(lead__email__iexact=user_email) | Q(lead__phone=request.user.username)
    ).filter(status__in=['sent', 'under_discussion', 'approved', 'rejected']).distinct()

    if request.method == 'POST':
        proposal_id = request.POST.get('proposal_id')
        action = request.POST.get('action')
        prop = get_object_or_404(Estimate, id=proposal_id)

        if action == 'accept':
            prop.status = 'approved'
            prop.save(update_fields=['status'])
            messages.success(request, f"Proposal {prop.estimate_number} has been officially accepted! Our project team will contact you for agreement execution.")
        elif action == 'reject':
            prop.status = 'rejected'
            prop.save(update_fields=['status'])
            messages.info(request, f"Proposal {prop.estimate_number} marked as declined.")
        return redirect('core:portal_proposals')

    return render(request, 'portal/proposals.html', {'proposals': proposals, 'pay_settings': PaymentSettings.load()})


@login_required(login_url='/portal/login/')
def portal_payments(request):
    """Customer Portal Payment History & Tax Receipts"""
    user_email = request.user.email or request.user.username
    requests_qs = PaymentRequest.objects.filter(
        Q(customer_email__iexact=user_email) | Q(lead__email__iexact=user_email)
    ).distinct()
    transactions = PaymentTransaction.objects.filter(
        Q(customer_email__iexact=user_email) | Q(lead__email__iexact=user_email)
    ).distinct()

    context = {
        'payment_requests': requests_qs,
        'transactions': transactions,
        'pay_settings': PaymentSettings.load(),
    }
    return render(request, 'portal/payments.html', context)


@login_required(login_url='/portal/login/')
def portal_support(request):
    """Customer Support Tickets & Helpdesk"""
    user_email = request.user.email or request.user.username
    tickets = SupportTicket.objects.filter(
        Q(customer_user=request.user) | Q(customer_email__iexact=user_email)
    ).distinct()

    return render(request, 'portal/support.html', {'tickets': tickets})


@login_required(login_url='/portal/login/')
def portal_support_create(request):
    """Create a new customer support ticket"""
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        category = request.POST.get('category', 'project_progress')
        priority = request.POST.get('priority', 'MEDIUM')
        description = request.POST.get('description', '').strip()
        project_id = request.POST.get('project_id')

        project = Project.objects.filter(id=project_id).first() if project_id else None

        ticket = SupportTicket.objects.create(
            customer_user=request.user,
            customer_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            customer_email=request.user.email,
            customer_phone=request.user.username,
            project=project,
            category=category,
            priority=priority,
            subject=subject,
            description=description,
            status='OPEN'
        )

        messages.success(request, f"Support Ticket {ticket.ticket_id} created successfully! Our engineering desk will respond shortly.")
        return redirect('core:portal_support_detail', ticket_id=ticket.ticket_id)

    user_email = request.user.email or request.user.username
    projects = Project.objects.filter(Q(customer_user=request.user) | Q(customer_email__iexact=user_email))
    return render(request, 'portal/support_create.html', {'projects': projects})


@login_required(login_url='/portal/login/')
def portal_support_detail(request, ticket_id):
    """Threaded Ticket Discussion"""
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)

    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        attachment = request.FILES.get('attachment')

        if message_text or attachment:
            SupportTicketMessage.objects.create(
                ticket=ticket,
                sender_user=request.user,
                sender_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                message=message_text,
                attachment=attachment,
                is_staff_reply=False
            )
            ticket.status = 'IN_PROGRESS'
            ticket.save(update_fields=['status', 'updated_at'])
            messages.success(request, "Your reply has been sent.")
            return redirect('core:portal_support_detail', ticket_id=ticket.ticket_id)

    return render(request, 'portal/support_detail.html', {'ticket': ticket})
