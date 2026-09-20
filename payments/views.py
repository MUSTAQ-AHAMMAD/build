import json
import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone

from .models import (
    PaymentSettings, PaymentGateway, PaymentMethod, UPIConfiguration,
    ServicePaymentConfiguration, PaymentRequest, PaymentTransaction,
    ProjectPaymentMilestone, ManualPaymentProof, PaymentReceipt,
    PaymentRefund, PaymentAuditLog
)
from .services import PaymentService
from .adapters import GatewayFactory
from .forms import (
    PaymentRequestForm, PaymentGatewayForm, UPIConfigurationForm,
    ServicePaymentConfigForm, ManualProofSubmissionForm, PaymentSettingsForm
)
from services.models import Service
from projects.models import Project
from crm.models import Lead, Estimate

def staff_required(user):
    return user.is_active and user.is_staff


# ==============================================================================
# PUBLIC CHECKOUT & PAYMENT FLOW
# ==============================================================================

@ensure_csrf_cookie
def public_payment_page(request, token):
    """Public secure checkout landing page"""
    req = get_object_or_404(PaymentRequest, uuid=token)
    
    if req.status == 'PAID':
        return redirect('payments:public_success', token=req.uuid)

    settings = PaymentSettings.load()
    upi_cfg = UPIConfiguration.load()
    gateways = PaymentGateway.objects.filter(is_active=True)
    methods = PaymentMethod.objects.filter(is_active=True)

    # Pre-generate UPI URI for instant QR/intent preview
    upi_uri = upi_cfg.get_upi_uri(
        amount=req.total_amount,
        note=f"{req.payment_purpose} ({req.payment_reference})",
        reference=req.payment_reference
    )

    context = {
        'payment_request': req,
        'settings': settings,
        'upi_cfg': upi_cfg,
        'upi_uri': upi_uri,
        'gateways': gateways,
        'methods': methods,
    }
    return render(request, 'payments/checkout.html', context)


@csrf_exempt
def public_initiate_checkout(request, token):
    """AJAX endpoint to initiate payment and fetch gateway adapter payload"""
    if request.method != 'POST':
        return HttpResponseBadRequest("POST required")

    req = get_object_or_404(PaymentRequest, uuid=token)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    method_type = data.get('method_type', 'gateway')
    gateway_id = data.get('gateway_id')
    gateway = PaymentGateway.objects.filter(id=gateway_id, is_active=True).first() if gateway_id else None

    try:
        tx, checkout_data = PaymentService.initiate_transaction(
            payment_request=req,
            payment_method_type=method_type,
            gateway=gateway,
            request=request
        )
        return JsonResponse({
            'status': 'ok',
            'transaction_uuid': str(tx.uuid),
            'reference': tx.payment_reference,
            'checkout_data': checkout_data
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
def public_verify_payment(request, token):
    """Handles client return callback verification from gateway"""
    if request.method != 'POST':
        return HttpResponseBadRequest("POST required")

    req = get_object_or_404(PaymentRequest, uuid=token)

    try:
        payload = json.loads(request.body)
    except Exception:
        payload = request.POST

    tx_uuid = payload.get('transaction_uuid')
    tx = PaymentTransaction.objects.filter(payment_request=req).first()
    if tx_uuid:
        tx = PaymentTransaction.objects.filter(uuid=tx_uuid, payment_request=req).first() or tx

    if not tx:
        return JsonResponse({'status': 'error', 'message': 'Transaction record not found'}, status=404)

    adapter = GatewayFactory.get_adapter(tx.gateway, method_type=tx.payment_method_type)
    is_valid, msg = adapter.verify_payment(tx, payload)

    if is_valid:
        receipt = PaymentService.complete_successful_payment(
            transaction_obj=tx,
            provider_tx_id=tx.provider_transaction_id,
            raw_response=payload,
            payment_method_name=tx.gateway.name if tx.gateway else 'Online Gateway'
        )
        return JsonResponse({
            'status': 'ok',
            'redirect_url': f"/pay/{req.uuid}/success/",
            'receipt_number': receipt.receipt_number
        })
    else:
        PaymentService.record_failed_payment(tx, failure_reason=msg, raw_response=payload)
        return JsonResponse({
            'status': 'failed',
            'redirect_url': f"/pay/{req.uuid}/failed/",
            'message': msg
        }, status=400)


def public_manual_proof_submit(request, token):
    """Customer submission of bank transfer / UPI UTR reference and screenshot"""
    req = get_object_or_404(PaymentRequest, uuid=token)

    if request.method == 'POST':
        tx, _ = PaymentService.initiate_transaction(
            payment_request=req,
            payment_method_type='bank_transfer',
            request=request
        )

        form = ManualProofSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            proof = form.save(commit=False)
            proof.payment_transaction = tx
            proof.payment_reference = req.payment_reference
            proof.status = 'PENDING'
            proof.save()

            tx.status = 'PENDING'
            tx.provider_transaction_id = proof.bank_reference
            tx.save(update_fields=['status', 'provider_transaction_id', 'updated_at'])

            messages.success(request, "Your payment proof has been submitted for manual verification. Our accounts desk will verify it shortly.")
            return redirect('payments:public_pending', token=req.uuid)
        else:
            messages.error(request, "Please enter a valid bank reference or UTR number.")

    return redirect('payments:public_pay', token=req.uuid)


def public_payment_success(request, token):
    """Public payment verified success page with receipt preview"""
    req = get_object_or_404(PaymentRequest, uuid=token)
    tx = req.transactions.filter(status='SUCCESS').first()
    receipt = getattr(tx, 'receipt', None) if tx else None

    context = {
        'payment_request': req,
        'transaction': tx,
        'receipt': receipt,
        'settings': PaymentSettings.load()
    }
    return render(request, 'payments/payment_success.html', context)


def public_payment_failed(request, token):
    """Payment failure notice page with retry actions"""
    req = get_object_or_404(PaymentRequest, uuid=token)
    tx = req.transactions.filter(status='FAILED').first()

    context = {
        'payment_request': req,
        'transaction': tx,
        'settings': PaymentSettings.load()
    }
    return render(request, 'payments/payment_failed.html', context)


def public_payment_pending(request, token):
    """Pending verification page for manual proofs and offline transfers"""
    req = get_object_or_404(PaymentRequest, uuid=token)
    tx = req.transactions.filter(status__in=['PENDING', 'CREATED', 'SUCCESS']).first()

    if tx and tx.status == 'SUCCESS':
        return redirect('payments:public_success', token=req.uuid)

    context = {
        'payment_request': req,
        'transaction': tx,
        'settings': PaymentSettings.load()
    }
    return render(request, 'payments/payment_pending.html', context)


def public_view_receipt(request, receipt_number):
    """Printable, branded formal payment receipt view"""
    receipt = get_object_or_404(PaymentReceipt, receipt_number=receipt_number)
    settings = PaymentSettings.load()

    context = {
        'receipt': receipt,
        'settings': settings,
    }
    return render(request, 'payments/payment_receipt.html', context)


@csrf_exempt
def payment_webhook_handler(request, gateway_slug):
    """Generic webhook endpoint for asynchronous payment gateway notifications"""
    if request.method != 'POST':
        return HttpResponseBadRequest("POST required")

    gateway = get_object_or_404(PaymentGateway, slug=gateway_slug)
    adapter = GatewayFactory.get_adapter(gateway)

    sig = request.META.get('HTTP_X_RAZORPAY_SIGNATURE') or request.META.get('HTTP_STRIPE_SIGNATURE', '')
    is_valid = adapter.verify_webhook(request.body, sig)

    if not is_valid:
        return HttpResponseBadRequest("Signature verification failed")

    try:
        payload = json.loads(request.body)
    except Exception:
        payload = request.POST

    result = adapter.process_webhook(payload)
    tx_id = result.get('provider_transaction_id')
    
    tx = PaymentTransaction.objects.filter(provider_transaction_id=tx_id).first()
    if tx and result.get('status') == 'SUCCESS':
        PaymentService.complete_successful_payment(
            transaction_obj=tx,
            provider_tx_id=tx_id,
            raw_response=payload,
            payment_method_name=gateway.name
        )

    return HttpResponse("Webhook processed", status=200)


# ==============================================================================
# CMS / ADMIN PAYMENT MANAGEMENT & ANALYTICS
# ==============================================================================

@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_payment_dashboard(request):
    """Executive Revenue & Payment Analytics Dashboard"""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Revenue Totals
    total_rev = PaymentTransaction.objects.filter(status='SUCCESS').aggregate(total=Sum('total_amount'))['total'] or 0
    today_rev = PaymentTransaction.objects.filter(status='SUCCESS', completed_at__gte=today_start).aggregate(total=Sum('total_amount'))['total'] or 0
    month_rev = PaymentTransaction.objects.filter(status='SUCCESS', completed_at__gte=month_start).aggregate(total=Sum('total_amount'))['total'] or 0

    # Counts
    total_tx = PaymentTransaction.objects.count()
    success_tx = PaymentTransaction.objects.filter(status='SUCCESS').count()
    pending_tx = PaymentTransaction.objects.filter(status__in=['PENDING', 'MANUAL_REVIEW']).count()
    failed_tx = PaymentTransaction.objects.filter(status='FAILED').count()

    success_rate = round((success_tx / total_tx * 100), 1) if total_tx > 0 else 0

    # Service Revenue Breakdown
    service_rev = (
        PaymentTransaction.objects.filter(status='SUCCESS', service__isnull=False)
        .values('service__name')
        .annotate(total=Sum('total_amount'), count=Count('id'))
        .order_by('-total')[:6]
    )

    # Recent Transactions
    recent_transactions = PaymentTransaction.objects.select_related('payment_request', 'gateway', 'service')[:10]

    context = {
        'total_rev': total_rev,
        'today_rev': today_rev,
        'month_rev': month_rev,
        'total_tx': total_tx,
        'success_tx': success_tx,
        'pending_tx': pending_tx,
        'failed_tx': failed_tx,
        'success_rate': success_rate,
        'service_rev': service_rev,
        'recent_transactions': recent_transactions,
        'settings': PaymentSettings.load(),
    }
    return render(request, 'payments/cms/dashboard.html', context)


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_transaction_list(request):
    """Searchable transaction stream with CSV export"""
    status_filter = request.GET.get('status', 'all')
    search_q = request.GET.get('q', '').strip()
    export_csv = request.GET.get('export') == 'csv'

    transactions = PaymentTransaction.objects.select_related('payment_request', 'gateway', 'service', 'lead').all()

    if status_filter != 'all':
        transactions = transactions.filter(status=status_filter.upper())

    if search_q:
        transactions = transactions.filter(
            Q(payment_reference__icontains=search_q) |
            Q(customer_name__icontains=search_q) |
            Q(customer_phone__icontains=search_q) |
            Q(provider_transaction_id__icontains=search_q)
        )

    if export_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="transactions_{timezone.now().strftime("%Y%m%d")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Reference', 'Customer', 'Phone', 'Service', 'Amount', 'Status', 'Gateway', 'Transaction ID', 'Date'])
        for t in transactions:
            writer.writerow([
                t.payment_reference, t.customer_name, t.customer_phone,
                t.service.name if t.service else '-', t.total_amount,
                t.status, t.gateway.name if t.gateway else 'Direct',
                t.provider_transaction_id, t.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        return response

    context = {
        'transactions': transactions[:60],
        'status_filter': status_filter,
        'search_q': search_q,
        'total_count': transactions.count(),
        'settings': PaymentSettings.load()
    }
    return render(request, 'payments/cms/transaction_list.html', context)


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_payment_requests(request):
    """Payment requests manager & generator"""
    requests_qs = PaymentRequest.objects.select_related('lead', 'project', 'service', 'estimate').all()
    status_filter = request.GET.get('status', 'all')

    if status_filter != 'all':
        requests_qs = requests_qs.filter(status=status_filter.upper())

    context = {
        'payment_requests': requests_qs[:50],
        'status_filter': status_filter,
        'total_count': requests_qs.count(),
        'settings': PaymentSettings.load()
    }
    return render(request, 'payments/cms/request_list.html', context)


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_payment_request_create(request):
    """Create new payment request linked to Customer / Lead / Project / Estimate"""
    if request.method == 'POST':
        form = PaymentRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.created_by = request.user
            req.save()
            messages.success(request, f"Payment Request {req.payment_reference} created successfully!")
            return redirect('payments:cms_requests')
    else:
        lead_id = request.GET.get('lead')
        estimate_id = request.GET.get('estimate')
        initial = {}
        if lead_id:
            lead = Lead.objects.filter(id=lead_id).first()
            if lead:
                initial['lead'] = lead
                initial['customer_name'] = lead.full_name
                initial['customer_phone'] = lead.phone
                initial['customer_email'] = lead.email
        if estimate_id:
            est = Estimate.objects.filter(id=estimate_id).first()
            if est:
                initial['estimate'] = est
                initial['amount'] = est.estimated_amount
                initial['tax_amount'] = est.tax_amount
                initial['total_amount'] = est.total_amount
                initial['payment_purpose'] = f"Estimate {est.estimate_number}: {est.description}"

        form = PaymentRequestForm(initial=initial)

    return render(request, 'payments/cms/request_form.html', {'form': form, 'settings': PaymentSettings.load()})


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_manual_verification_desk(request):
    """Staff verification desk for manual bank transfer slips & offline proofs"""
    if request.method == 'POST':
        proof_id = request.POST.get('proof_id')
        action = request.POST.get('action')
        notes = request.POST.get('rejection_notes', '')

        proof = get_object_or_404(ManualPaymentProof, id=proof_id)
        if action == 'approve':
            PaymentService.verify_manual_proof(proof, is_approved=True, user=request.user)
            messages.success(request, f"Payment {proof.payment_reference} verified and settled successfully!")
        elif action == 'reject':
            PaymentService.verify_manual_proof(proof, is_approved=False, user=request.user, rejection_notes=notes)
            messages.warning(request, f"Payment {proof.payment_reference} marked as rejected.")
        return redirect('payments:cms_manual_verification')

    proofs = ManualPaymentProof.objects.select_related('payment_transaction', 'verified_by').all()
    status_filter = request.GET.get('status', 'PENDING')
    if status_filter != 'all':
        proofs = proofs.filter(status=status_filter)

    context = {
        'proofs': proofs,
        'status_filter': status_filter,
        'settings': PaymentSettings.load()
    }
    return render(request, 'payments/cms/manual_verification.html', context)


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_refunds_manager(request):
    """Refund management & approvals"""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_refund':
            tx_id = request.POST.get('transaction_id')
            tx = get_object_or_404(PaymentTransaction, id=tx_id)
            amount = float(request.POST.get('amount', tx.total_amount))
            reason = request.POST.get('reason', '')
            
            ref = PaymentRefund.objects.create(
                payment_transaction=tx,
                requested_amount=amount,
                reason=reason,
                requested_by=request.user,
                status='REQUESTED'
            )
            messages.success(request, f"Refund request {ref.refund_reference} submitted.")
        elif action == 'approve_refund':
            ref_id = request.POST.get('refund_id')
            ref = get_object_or_404(PaymentRefund, id=ref_id)
            ref.status = 'COMPLETED'
            ref.approved_amount = ref.requested_amount
            ref.approved_by = request.user
            ref.completed_at = timezone.now()
            ref.gateway_refund_id = f"GW_REF_{timezone.now().strftime('%Y%m%d%H%M')}"
            ref.save()

            ref.payment_transaction.status = 'REFUNDED'
            ref.payment_transaction.save(update_fields=['status', 'updated_at'])
            messages.success(request, f"Refund {ref.refund_reference} approved and executed.")
        return redirect('payments:cms_refunds')

    refunds = PaymentRefund.objects.select_related('payment_transaction', 'requested_by', 'approved_by').all()
    context = {'refunds': refunds, 'settings': PaymentSettings.load()}
    return render(request, 'payments/cms/refund_list.html', context)


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_gateways_list(request):
    """Payment gateways directory & status controls"""
    gateways = PaymentGateway.objects.all()
    return render(request, 'payments/cms/gateway_list.html', {'gateways': gateways, 'settings': PaymentSettings.load()})


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_gateway_edit(request, gateway_id=None):
    """Add / Edit payment gateway credentials and custom embed code"""
    gateway = get_object_or_404(PaymentGateway, id=gateway_id) if gateway_id else None

    if request.method == 'POST':
        form = PaymentGatewayForm(request.POST, instance=gateway)
        if form.is_valid():
            gw = form.save()
            messages.success(request, f"Gateway {gw.name} configured successfully!")
            return redirect('payments:cms_gateways')
    else:
        form = PaymentGatewayForm(instance=gateway)

    return render(request, 'payments/cms/gateway_form.html', {'form': form, 'gateway': gateway, 'settings': PaymentSettings.load()})


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_upi_config(request):
    """UPI Virtual Payment Address & QR code manager"""
    upi_obj = UPIConfiguration.load()

    if request.method == 'POST':
        form = UPIConfigurationForm(request.POST, request.FILES, instance=upi_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "UPI payment configuration updated successfully.")
            return redirect('payments:cms_upi')
    else:
        form = UPIConfigurationForm(instance=upi_obj)

    return render(request, 'payments/cms/upi_settings.html', {'form': form, 'upi_cfg': upi_obj, 'settings': PaymentSettings.load()})


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_service_pricing(request):
    """Service-specific payment settings (advance %, consultation fee, site visit fee)"""
    services = Service.objects.select_related('payment_config').all()

    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        service = get_object_or_404(Service, id=service_id)
        config, _ = ServicePaymentConfiguration.objects.get_or_create(service=service)

        config.payment_enabled = request.POST.get('payment_enabled') == 'on'
        config.payment_type = request.POST.get('payment_type', 'fixed')
        config.fixed_amount = request.POST.get('fixed_amount', config.fixed_amount)
        config.advance_percentage = request.POST.get('advance_percentage', config.advance_percentage)
        config.consultation_fee = request.POST.get('consultation_fee', config.consultation_fee)
        config.site_visit_fee = request.POST.get('site_visit_fee', config.site_visit_fee)
        config.display_payment_button = request.POST.get('display_payment_button') == 'on'
        config.save()

        messages.success(request, f"Payment settings updated for {service.name}.")
        return redirect('payments:cms_service_pricing')

    return render(request, 'payments/cms/service_pricing.html', {'services': services, 'settings': PaymentSettings.load()})


@login_required(login_url='/cms/login/')
@user_passes_test(staff_required, login_url='/cms/login/')
def cms_payment_settings(request):
    """Global Payment Settings & GST Configuration"""
    settings_obj = PaymentSettings.load()

    if request.method == 'POST':
        form = PaymentSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Global payment settings saved.")
            return redirect('payments:cms_settings')
    else:
        form = PaymentSettingsForm(instance=settings_obj)

    return render(request, 'payments/cms/settings.html', {'form': form, 'settings': settings_obj})
