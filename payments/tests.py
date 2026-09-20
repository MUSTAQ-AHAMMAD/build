import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

from .models import (
    PaymentSettings, PaymentGateway, PaymentMethod, UPIConfiguration,
    ServicePaymentConfiguration, PaymentRequest, PaymentTransaction,
    ProjectPaymentMilestone, ManualPaymentProof, PaymentReceipt,
    PaymentRefund, PaymentAuditLog
)
from .services import PaymentService
from .adapters import RazorpayAdapter, UPIAdapter, GatewayFactory
from services.models import Service, ServiceCategory
from crm.models import Lead

class PaymentSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(username='staff_test', password='password123', is_staff=True)
        self.normal_user = User.objects.create_user(username='normal_user', password='password123', is_staff=False)

        self.category = ServiceCategory.objects.create(name="Renovation", slug="renovation")
        self.service = Service.objects.create(
            name="Flat Renovation",
            slug="flat-renovation",
            category=self.category,
            short_description="Turnkey flat renovation"
        )

        self.lead = Lead.objects.create(
            first_name="Anita",
            last_name="Desai",
            phone="+91 98888 77777",
            email="anita.desai@example.com",
            service_category="renovation",
            service_type="flat_renovation",
            property_location="Banjara Hills, Hyderabad"
        )

        self.gateway = PaymentGateway.objects.create(
            name="Test Razorpay",
            provider_name="Razorpay",
            gateway_type="HOSTED_CHECKOUT",
            is_active=True,
            is_default=True,
            is_test_mode=True,
            public_key="rzp_test_public_key_123",
            encrypted_secret_key="secret_test_key"
        )

        self.payment_request = PaymentRequest.objects.create(
            customer_name="Anita Desai",
            customer_phone="+91 98888 77777",
            customer_email="anita.desai@example.com",
            lead=self.lead,
            service=self.service,
            payment_purpose="Flat Renovation Site Visit Fee",
            amount=Decimal('2000.00'),
            tax_amount=Decimal('360.00'),
            total_amount=Decimal('2360.00'),
            status='PENDING'
        )

    def test_payment_settings_and_upi_config_loading(self):
        settings = PaymentSettings.load()
        self.assertIsNotNone(settings)
        self.assertEqual(settings.currency, "INR")

        upi_cfg = UPIConfiguration.load()
        self.assertIsNotNone(upi_cfg)
        uri = upi_cfg.get_upi_uri(amount=2000.0, note="Test Inspection", reference="PAY-2026-TEST")
        self.assertTrue(uri.startswith("upi://pay?"))
        self.assertIn("pa=", uri)
        self.assertIn("am=2000.00", uri)

    def test_payment_request_reference_generation(self):
        self.assertTrue(self.payment_request.payment_reference.startswith("PAY-"))
        self.assertEqual(self.payment_request.total_amount, Decimal('2360.00'))
        self.assertFalse(self.payment_request.is_expired)

    def test_payment_service_initiate_transaction(self):
        tx, checkout_data = PaymentService.initiate_transaction(
            payment_request=self.payment_request,
            payment_method_type='gateway',
            gateway=self.gateway
        )
        self.assertEqual(tx.status, 'CREATED')
        self.assertEqual(tx.total_amount, Decimal('2360.00'))
        self.assertIn('amount', checkout_data)
        self.assertEqual(checkout_data['amount'], 236000) # In paise

    def test_payment_service_complete_successful_payment(self):
        tx, _ = PaymentService.initiate_transaction(
            payment_request=self.payment_request,
            payment_method_type='gateway',
            gateway=self.gateway
        )
        receipt = PaymentService.complete_successful_payment(
            transaction_obj=tx,
            provider_tx_id="pay_RZP_TEST_12345",
            payment_method_name="Razorpay Online"
        )
        self.assertEqual(tx.status, 'SUCCESS')
        self.assertEqual(self.payment_request.status, 'PAID')
        self.assertIsNotNone(receipt)
        self.assertTrue(receipt.receipt_number.startswith("REC-"))
        self.assertEqual(receipt.total_paid, Decimal('2360.00'))

        # Check LeadActivity logged
        lead_activities = self.lead.activities.filter(activity_type='created')
        self.assertTrue(lead_activities.exists())

    def test_public_checkout_and_ajax_endpoints(self):
        # 1. Public Payment Page
        resp = self.client.get(f"/pay/{self.payment_request.uuid}/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.payment_request.payment_reference)
        self.assertContains(resp, "2360.00")

        # 2. AJAX Checkout Initiate
        checkout_resp = self.client.post(
            f"/pay/{self.payment_request.uuid}/checkout/",
            data=json.dumps({'method_type': 'gateway'}),
            content_type='application/json'
        )
        self.assertEqual(checkout_resp.status_code, 200)
        data = checkout_resp.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('transaction_uuid', data)

        # 3. AJAX Verification
        verify_resp = self.client.post(
            f"/pay/{self.payment_request.uuid}/verify/",
            data=json.dumps({
                'transaction_uuid': data['transaction_uuid'],
                'razorpay_payment_id': 'pay_simulated_test_999',
                'razorpay_order_id': 'order_test_999'
            }),
            content_type='application/json'
        )
        self.assertEqual(verify_resp.status_code, 200)
        self.assertEqual(verify_resp.json()['status'], 'ok')

        # 4. Success page
        succ_resp = self.client.get(f"/pay/{self.payment_request.uuid}/success/")
        self.assertEqual(succ_resp.status_code, 200)
        self.assertContains(succ_resp, "Payment Successfully Verified")

    def test_public_manual_proof_submit(self):
        resp = self.client.post(
            f"/pay/{self.payment_request.uuid}/manual-submit/",
            data={
                'method': 'bank_transfer',
                'bank_reference': 'UTR-NEFT-9988776655',
                'notes': 'Paid from ICICI Bank account.'
            }
        )
        self.assertEqual(resp.status_code, 302)
        
        proof = ManualPaymentProof.objects.filter(bank_reference='UTR-NEFT-9988776655').first()
        self.assertIsNotNone(proof)
        self.assertEqual(proof.status, 'PENDING')

    def test_cms_payment_dashboard_and_permissions(self):
        # Anonymous blocked
        anon_resp = self.client.get('/cms/payments/')
        self.assertIn(anon_resp.status_code, [302, 403])

        # Staff allowed
        self.client.force_login(self.staff_user)
        staff_resp = self.client.get('/cms/payments/')
        self.assertEqual(staff_resp.status_code, 200)
        self.assertContains(staff_resp, "Revenue & Payments Management")

        # Check endpoints
        self.assertEqual(self.client.get('/cms/payments/transactions/').status_code, 200)
        self.assertEqual(self.client.get('/cms/payments/requests/').status_code, 200)
        self.assertEqual(self.client.get('/cms/payments/manual-verification/').status_code, 200)
        self.assertEqual(self.client.get('/cms/payments/refunds/').status_code, 200)
        self.assertEqual(self.client.get('/cms/payments/gateways/').status_code, 200)
        self.assertEqual(self.client.get('/cms/payments/upi/').status_code, 200)
        self.assertEqual(self.client.get('/cms/payments/services-pricing/').status_code, 200)
        self.assertEqual(self.client.get('/cms/payments/settings/').status_code, 200)

    def test_cms_manual_proof_approval(self):
        tx, _ = PaymentService.initiate_transaction(
            payment_request=self.payment_request,
            payment_method_type='bank_transfer'
        )
        proof = ManualPaymentProof.objects.create(
            payment_transaction=tx,
            payment_reference=self.payment_request.payment_reference,
            method='bank_transfer',
            bank_reference='UTR-12345678',
            status='PENDING'
        )

        self.client.force_login(self.staff_user)
        post_resp = self.client.post(
            '/cms/payments/manual-verification/',
            data={'proof_id': proof.id, 'action': 'approve'}
        )
        self.assertEqual(post_resp.status_code, 302)

        proof.refresh_from_db()
        self.assertEqual(proof.status, 'VERIFIED')
        self.assertEqual(proof.payment_transaction.status, 'SUCCESS')
        self.payment_request.refresh_from_db()
        self.assertEqual(self.payment_request.status, 'PAID')
