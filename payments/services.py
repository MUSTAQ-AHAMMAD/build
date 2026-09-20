from django.utils import timezone
from django.db import transaction as db_transaction
from .models import (
    PaymentSettings, PaymentGateway, PaymentMethod, PaymentRequest,
    PaymentTransaction, PaymentReceipt, PaymentRefund, PaymentAuditLog,
    ManualPaymentProof
)
from .adapters import GatewayFactory
from crm.models import LeadActivity, SiteVisit

class PaymentService:
    """Core Payment Orchestration Layer"""

    @classmethod
    def initiate_transaction(cls, payment_request, payment_method_type='gateway', gateway=None, payment_method=None, request=None):
        """Creates or reuses an initiated transaction and retrieves adapter checkout payload"""
        if payment_request.is_expired:
            payment_request.status = 'EXPIRED'
            payment_request.save(update_fields=['status'])
            raise ValueError("This payment request has expired.")

        if payment_request.status == 'PAID':
            raise ValueError("This payment request has already been paid and settled.")

        # Check for existing initiated/pending transaction within last 30 minutes
        existing_tx = PaymentTransaction.objects.filter(
            payment_request=payment_request,
            status__in=['CREATED', 'PENDING'],
            payment_method_type=payment_method_type
        ).first()

        if existing_tx:
            tx = existing_tx
        else:
            tx = PaymentTransaction.objects.create(
                payment_reference=payment_request.payment_reference,
                payment_request=payment_request,
                customer_name=payment_request.customer_name,
                customer_email=payment_request.customer_email,
                customer_phone=payment_request.customer_phone,
                lead=payment_request.lead,
                project=payment_request.project,
                service=payment_request.service,
                gateway=gateway or payment_request.preferred_gateway or PaymentGateway.objects.filter(is_default=True, is_active=True).first(),
                payment_method=payment_method,
                payment_method_type=payment_method_type,
                amount=payment_request.amount,
                tax_amount=payment_request.tax_amount,
                discount_amount=payment_request.discount_amount,
                total_amount=payment_request.total_amount,
                currency=payment_request.currency,
                status='CREATED',
                is_test_mode=gateway.is_test_mode if gateway else True,
            )

            PaymentAuditLog.objects.create(
                payment_transaction=tx,
                payment_request=payment_request,
                action="PAYMENT_INITIATED",
                new_status="CREATED",
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={'method': payment_method_type}
            )

        # Get adapter
        adapter = GatewayFactory.get_adapter(tx.gateway, method_type=payment_method_type)
        checkout_data = adapter.create_order(tx, request=request)

        return tx, checkout_data

    @classmethod
    @db_transaction.atomic
    def complete_successful_payment(cls, transaction_obj, provider_tx_id, raw_response=None, user=None, payment_method_name=None):
        """Marks transaction as successful, creates receipt, and updates CRM state"""
        if transaction_obj.status == 'SUCCESS':
            return transaction_obj.receipt

        old_status = transaction_obj.status
        transaction_obj.status = 'SUCCESS'
        transaction_obj.completed_at = timezone.now()
        transaction_obj.provider_transaction_id = provider_tx_id or f"TXN_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        if raw_response:
            transaction_obj.payment_response_json = raw_response
        transaction_obj.save()

        # Update Payment Request
        req = transaction_obj.payment_request
        req.status = 'PAID'
        req.save(update_fields=['status', 'updated_at'])

        # Generate Formal Payment Receipt
        settings = PaymentSettings.load()
        method_name = payment_method_name or (transaction_obj.payment_method.display_name if transaction_obj.payment_method else transaction_obj.get_payment_method_type_display())
        
        receipt = PaymentReceipt.objects.create(
            payment_transaction=transaction_obj,
            customer_name=transaction_obj.customer_name,
            customer_email=transaction_obj.customer_email,
            customer_phone=transaction_obj.customer_phone,
            service_name=transaction_obj.service.name if transaction_obj.service else (transaction_obj.lead.service_type if transaction_obj.lead else 'Construction Service'),
            project_name=transaction_obj.project.title if transaction_obj.project else '',
            payment_purpose=req.payment_purpose,
            amount=transaction_obj.amount,
            tax_amount=transaction_obj.tax_amount,
            total_paid=transaction_obj.total_amount,
            currency=transaction_obj.currency,
            payment_method_name=method_name,
            gateway_name=transaction_obj.gateway.name if transaction_obj.gateway else 'Direct / UPI',
            provider_transaction_id=transaction_obj.provider_transaction_id,
            notes=f"Payment verified and settled for {req.payment_reference}."
        )

        # Update Linked Project Milestones
        if transaction_obj.project:
            milestone = transaction_obj.project.payment_milestones.filter(payment_request=req).first()
            if milestone:
                milestone.status = 'PAID'
                milestone.payment_transaction = transaction_obj
                milestone.save(update_fields=['status', 'payment_transaction', 'updated_at'])

        # Synchronize with CRM Lead
        if transaction_obj.lead:
            LeadActivity.objects.create(
                lead=transaction_obj.lead,
                activity_type='created',
                title=f"Payment Cleared: ₹{transaction_obj.total_amount:,.2f} ({req.payment_reference})",
                description=f"Payment of ₹{transaction_obj.total_amount:,.2f} verified via {method_name}. Receipt No: {receipt.receipt_number}."
            )

            # Auto-confirm Site Visit if purpose is site visit
            if 'site visit' in req.payment_purpose.lower() or 'inspection' in req.payment_purpose.lower():
                sv = transaction_obj.lead.site_visits.filter(status='scheduled').first()
                if sv:
                    sv.notes = f"{sv.notes}\n[PAID] Site visit fee ₹{transaction_obj.total_amount:,.2f} cleared."
                    sv.save(update_fields=['notes'])

        # Audit Log
        PaymentAuditLog.objects.create(
            user=user,
            payment_transaction=transaction_obj,
            payment_request=req,
            action="PAYMENT_SUCCESS",
            old_status=old_status,
            new_status="SUCCESS",
            metadata={'receipt_number': receipt.receipt_number, 'provider_tx_id': transaction_obj.provider_transaction_id}
        )

        return receipt

    @classmethod
    def record_failed_payment(cls, transaction_obj, failure_reason="Payment declined by user or provider", raw_response=None):
        """Marks transaction as failed"""
        old_status = transaction_obj.status
        transaction_obj.status = 'FAILED'
        transaction_obj.failure_reason = failure_reason
        if raw_response:
            transaction_obj.payment_response_json = raw_response
        transaction_obj.save(update_fields=['status', 'failure_reason', 'payment_response_json', 'updated_at'])

        PaymentAuditLog.objects.create(
            payment_transaction=transaction_obj,
            payment_request=transaction_obj.payment_request,
            action="PAYMENT_FAILED",
            old_status=old_status,
            new_status="FAILED",
            metadata={'reason': failure_reason}
        )

    @classmethod
    def verify_manual_proof(cls, proof_obj, is_approved, user, rejection_notes=''):
        """Processes manual payment proof verification by authorized staff"""
        proof_obj.verified_by = user
        proof_obj.verified_at = timezone.now()

        if is_approved:
            proof_obj.status = 'VERIFIED'
            proof_obj.save(update_fields=['status', 'verified_by', 'verified_at'])
            cls.complete_successful_payment(
                proof_obj.payment_transaction,
                provider_tx_id=proof_obj.bank_reference or f"MANUAL_{proof_obj.id}",
                user=user,
                payment_method_name=proof_obj.get_method_display()
            )
        else:
            proof_obj.status = 'REJECTED'
            proof_obj.rejection_reason = rejection_notes
            proof_obj.save(update_fields=['status', 'verified_by', 'verified_at', 'rejection_reason'])
            cls.record_failed_payment(
                proof_obj.payment_transaction,
                failure_reason=f"Manual verification rejected: {rejection_notes}"
            )
