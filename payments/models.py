import uuid
import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

from services.models import Service
from projects.models import Project
from crm.models import Lead, Estimate

class PaymentSettings(models.Model):
    """Global Corporate Payment & Invoicing Settings"""
    company_name = models.CharField(max_length=200, default="BUILD+ Construction & Infrastructure")
    company_address = models.TextField(default="Road No. 36, Jubilee Hills, Hyderabad, Telangana - 500033")
    currency = models.CharField(max_length=10, default="INR")
    currency_symbol = models.CharField(max_length=10, default="₹")
    gst_enabled = models.BooleanField(default=True)
    gst_number = models.CharField(max_length=50, default="36AAAAA0000A1Z5")
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    invoice_prefix = models.CharField(max_length=20, default="INV")
    receipt_prefix = models.CharField(max_length=20, default="REC")
    payment_request_prefix = models.CharField(max_length=20, default="PAY")
    is_test_mode_globally = models.BooleanField(default=False, help_text="Override all gateways to test mode")
    webhook_secret = models.CharField(max_length=255, blank=True)
    payment_terms = models.TextField(
        default="1. Milestone payments must be released as per signed BOQ schedule.\n2. Site inspection and consultation fees are non-refundable once site audit is conducted.\n3. All transactions are subject to standard GST."
    )
    refund_policy = models.TextField(
        default="Refunds for advance booking fees are processed within 7-10 business days subject to deduction of structural audit costs incurred."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment Settings"
        verbose_name_plural = "Payment Settings"

    def __str__(self):
        return f"{self.company_name} Payment Settings"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PaymentGateway(models.Model):
    """Gateway-agnostic payment provider configuration & custom code embed manager"""
    GATEWAY_TYPES = [
        ('HOSTED_CHECKOUT', 'Hosted Checkout Page (Razorpay / Stripe / PayU)'),
        ('EMBEDDED_CHECKOUT', 'Embedded Modal / Seamless Checkout'),
        ('HTML_SNIPPET', 'Custom Client-Side HTML Embed Code'),
        ('JAVASCRIPT_CHECKOUT', 'Custom JavaScript Provider Checkout'),
        ('UPI', 'Direct UPI ID / VPA Intent'),
        ('UPI_QR', 'Static / Dynamic UPI QR Code'),
        ('PAYMENT_LINK', 'Third-Party Payment Link Generator'),
        ('BANK_TRANSFER', 'Direct Bank NEFT / RTGS / IMPS'),
        ('MANUAL', 'Manual Cash / Cheque / Offline Verification'),
    ]

    name = models.CharField(max_length=120, help_text="e.g. Razorpay Live, PhonePe PG, Custom Gateway Embed")
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    provider_name = models.CharField(max_length=100, default="Razorpay", help_text="e.g. Razorpay, Stripe, Cashfree, PayU, PhonePe, Custom")
    gateway_type = models.CharField(max_length=30, choices=GATEWAY_TYPES, default='HOSTED_CHECKOUT')
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    is_test_mode = models.BooleanField(default=True, help_text="Check to use sandbox / test credentials")

    public_key = models.CharField(max_length=255, blank=True, help_text="Public Key / Key ID / Publishable Key")
    merchant_id = models.CharField(max_length=255, blank=True, help_text="Merchant ID / Client ID")
    encrypted_secret_key = models.CharField(max_length=255, blank=True, help_text="API Secret (Stored on server)")
    encrypted_api_key = models.CharField(max_length=255, blank=True, help_text="Secondary API Key if required")

    checkout_url = models.URLField(max_length=500, blank=True, help_text="Provider checkout endpoint")
    webhook_url = models.CharField(max_length=500, blank=True, help_text="Configured webhook listener URI")

    # Custom Code Embed for Non-Developer Integration
    custom_html = models.TextField(blank=True, help_text="Provider-approved HTML snippet or button code")
    custom_css = models.TextField(blank=True, help_text="Custom CSS styling for the payment container")
    custom_js = models.TextField(blank=True, help_text="Client-side JavaScript SDK initialization snippet")

    success_url = models.CharField(max_length=255, blank=True, default="/payments/success/")
    failure_url = models.CharField(max_length=255, blank=True, default="/payments/failed/")
    cancel_url = models.CharField(max_length=255, blank=True, default="/payments/cancelled/")

    documentation_url = models.URLField(blank=True, help_text="Provider official integration docs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', 'name']
        verbose_name = "Payment Gateway"
        verbose_name_plural = "Payment Gateways"

    def __str__(self):
        mode = "TEST" if self.is_test_mode else "LIVE"
        return f"{self.name} ({self.get_gateway_type_display()}) [{mode}]"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.is_default:
            PaymentGateway.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class PaymentMethod(models.Model):
    """Customer-facing Payment Selection Methods (Gateway, UPI, QR, Bank Transfer)"""
    METHOD_TYPES = [
        ('gateway', 'Card / NetBanking / Wallet via Gateway'),
        ('upi', 'UPI Mobile Intent / Apps'),
        ('qr', 'Scan & Pay QR Code'),
        ('bank_transfer', 'Direct Bank Transfer (NEFT / RTGS / IMPS)'),
        ('manual', 'Manual Cash / Cheque at Site Desk'),
    ]

    name = models.CharField(max_length=100)
    method_type = models.CharField(max_length=30, choices=METHOD_TYPES, default='gateway')
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, null=True, blank=True, related_name='methods')
    display_name = models.CharField(max_length=150, help_text="e.g. UPI (Google Pay, PhonePe, Paytm)")
    description = models.CharField(max_length=255, blank=True, help_text="e.g. Instant payment with zero gateway surcharge")
    instructions = models.TextField(blank=True, help_text="Specific payment instructions shown on checkout")
    icon = models.CharField(max_length=50, default="💳", help_text="Emoji or icon")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"

    def __str__(self):
        return f"{self.display_name} ({self.get_method_type_display()})"


class UPIConfiguration(models.Model):
    """Corporate UPI Virtual Payment Address & Dynamic QR Manager"""
    upi_id = models.CharField(max_length=120, default="buildplus@upi", help_text="e.g. company@icici or 9876543210@paytm")
    merchant_name = models.CharField(max_length=150, default="BUILD+ Construction & Infrastructure")
    display_name = models.CharField(max_length=150, default="BUILD+ Official UPI")
    qr_code_image = models.ImageField(upload_to='payments/upi_qr/', blank=True, null=True, help_text="Upload official pre-generated merchant QR image")
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_ifsc_code = models.CharField(max_length=30, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    payment_instructions = models.TextField(
        default="1. Scan QR or pay to UPI ID.\n2. Enter the exact payment amount.\n3. Enter the Reference Number in remarks.\n4. Take screenshot and submit UTR number."
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "UPI Configuration"
        verbose_name_plural = "UPI Configurations"

    def __str__(self):
        return f"{self.merchant_name} ({self.upi_id})"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_upi_uri(self, amount=None, note=None, reference=None):
        """Generates standard NPCI compliant upi://pay URI"""
        params = [
            f"pa={self.upi_id}",
            f"pn={self.merchant_name.replace(' ', '%20')}",
            "cu=INR"
        ]
        if amount:
            params.append(f"am={amount:.2f}")
        if note:
            params.append(f"tn={str(note)[:40].replace(' ', '%20')}")
        if reference:
            params.append(f"tr={reference}")
        return f"upi://pay?{'&'.join(params)}"


class ServicePaymentConfiguration(models.Model):
    """Service-specific fee, advance percentage, and payment enablement settings"""
    PAYMENT_TYPES = [
        ('fixed', 'Fixed Consultation / Service Fee'),
        ('percentage', 'Percentage Advance on Project Scope'),
        ('site_visit', 'On-Site Technical Inspection Fee'),
        ('advance', 'Initial Milestone Advance'),
        ('custom', 'Custom Dynamic Customer Stated Amount'),
    ]

    service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='payment_config')
    payment_enabled = models.BooleanField(default=True)
    payment_type = models.CharField(max_length=30, choices=PAYMENT_TYPES, default='fixed')
    fixed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=2000.00, help_text="Amount in ₹")
    advance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="e.g. 10% advance")
    minimum_amount = models.DecimalField(max_digits=12, decimal_places=2, default=500.00)
    allow_custom_amount = models.BooleanField(default=False)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    site_visit_fee = models.DecimalField(max_digits=10, decimal_places=2, default=2000.00)
    display_payment_button = models.BooleanField(default=True, help_text="Display Pay Now button on public service page")
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Service Payment Configuration"
        verbose_name_plural = "Service Payment Configurations"

    def __str__(self):
        return f"{self.service.name} Payment Config ({self.get_payment_type_display()})"


class PaymentRequest(models.Model):
    """Staff-generated or System-initiated Customer Payment Request"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid / Completed'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    payment_reference = models.CharField(max_length=40, unique=True, editable=False, db_index=True)
    
    # Customer Details
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=30)
    
    # Linked Entities
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_requests')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_requests')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_requests')
    estimate = models.ForeignKey(Estimate, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_requests')
    
    # Financials
    payment_purpose = models.CharField(max_length=255, default="Consultation & Site Inspection Fee")
    amount = models.DecimalField(max_digits=14, decimal_places=2, help_text="Subtotal in ₹")
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, help_text="GST in ₹")
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, help_text="Grand Total in ₹")
    currency = models.CharField(max_length=10, default="INR")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    preferred_gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_requests')
    due_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_payment_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Request"
        verbose_name_plural = "Payment Requests"

    def __str__(self):
        return f"{self.payment_reference} - {self.customer_name} (₹{self.total_amount:,.2f}) [{self.status}]"

    def save(self, *args, **kwargs):
        if not self.payment_reference:
            year_str = timezone.now().strftime('%Y')
            random_int = random.randint(100000, 999999)
            self.payment_reference = f"PAY-{year_str}-{random_int}"
            while PaymentRequest.objects.filter(payment_reference=self.payment_reference).exists():
                random_int = random.randint(100000, 999999)
                self.payment_reference = f"PAY-{year_str}-{random_int}"

        if not self.total_amount:
            self.total_amount = (self.amount or 0) + (self.tax_amount or 0) - (self.discount_amount or 0)

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        if self.expiry_date and timezone.now().date() > self.expiry_date and self.status == 'PENDING':
            return True
        return False


class PaymentTransaction(models.Model):
    """Core Payment Transaction Audit Record with Complete Gateway Lifecycle"""
    STATUS_CHOICES = [
        ('CREATED', 'Created / Initiated'),
        ('PENDING', 'Pending Verification'),
        ('AUTHORIZED', 'Authorized by Provider'),
        ('SUCCESS', 'Payment Successful'),
        ('FAILED', 'Payment Failed / Declined'),
        ('CANCELLED', 'Cancelled by User'),
        ('REFUNDED', 'Fully Refunded'),
        ('PARTIALLY_REFUNDED', 'Partially Refunded'),
        ('EXPIRED', 'Transaction Expired'),
        ('MANUAL_REVIEW', 'Manual Review Required'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    payment_reference = models.CharField(max_length=50, db_index=True)
    payment_request = models.ForeignKey(PaymentRequest, on_delete=models.CASCADE, related_name='transactions')

    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=30)

    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_transactions')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_transactions')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_transactions')

    gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    payment_method_type = models.CharField(max_length=40, default="gateway")

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='CREATED', db_index=True)
    is_test_mode = models.BooleanField(default=False)

    provider_transaction_id = models.CharField(max_length=255, blank=True, db_index=True, help_text="Gateway Payment ID / UTR")
    provider_order_id = models.CharField(max_length=255, blank=True, db_index=True, help_text="Gateway Order ID")
    payment_response_json = models.JSONField(default=dict, blank=True, help_text="Full raw response payload from gateway")
    failure_reason = models.TextField(blank=True)

    initiated_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"

    def __str__(self):
        return f"{self.payment_reference} - ₹{self.total_amount:,.2f} [{self.status}]"


class ProjectPaymentMilestone(models.Model):
    """Construction & Renovation Project Stage Milestone Billing"""
    MILESTONE_STATUSES = [
        ('PENDING', 'Pending Initiation'),
        ('DUE', 'Due for Payment'),
        ('PAID', 'Paid & Cleared'),
        ('OVERDUE', 'Overdue'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payment_milestones')
    milestone_name = models.CharField(max_length=150, help_text="e.g. Foundation & Plinth Completion")
    description = models.TextField(blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="e.g. 15.00%")
    amount = models.DecimalField(max_digits=14, decimal_places=2, help_text="Amount in ₹")
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=MILESTONE_STATUSES, default='PENDING')

    payment_request = models.ForeignKey(PaymentRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='milestones')
    payment_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='milestones')

    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['project', 'display_order', 'due_date']
        verbose_name = "Project Payment Milestone"
        verbose_name_plural = "Project Payment Milestones"

    def __str__(self):
        return f"{self.project.title} - {self.milestone_name} ({self.percentage}% = ₹{self.amount:,.2f})"


class ManualPaymentProof(models.Model):
    """Proof Documents and Staff Verification for Offline / Bank Transfer Payments"""
    PROOF_STATUSES = [
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified & Cleared'),
        ('REJECTED', 'Rejected'),
    ]

    PAYMENT_MODES = [
        ('bank_transfer', 'Bank Transfer (NEFT/RTGS/IMPS)'),
        ('upi_manual', 'Manual UPI Transaction Screenshot'),
        ('cheque', 'Cheque Deposit'),
        ('cash', 'Direct Cash at Branch'),
        ('other', 'Other Offline Mode'),
    ]

    payment_transaction = models.OneToOneField(PaymentTransaction, on_delete=models.CASCADE, related_name='manual_proof')
    payment_reference = models.CharField(max_length=50)
    method = models.CharField(max_length=30, choices=PAYMENT_MODES, default='bank_transfer')
    bank_reference = models.CharField(max_length=100, blank=True, help_text="UTR / Cheque Number / Transaction Reference")
    notes = models.TextField(blank=True)
    proof_document = models.FileField(upload_to='payments/proofs/%Y/%m/', blank=True, null=True, help_text="Receipt screenshot, counterfoil, or bank slip")
    status = models.CharField(max_length=20, choices=PROOF_STATUSES, default='PENDING', db_index=True)

    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_manual_payments')
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Manual Payment Proof"
        verbose_name_plural = "Manual Payment Proofs"

    def __str__(self):
        return f"Proof for {self.payment_reference} [{self.status}]"


class PaymentReceipt(models.Model):
    """Formal Corporate Payment Receipt with GST & Printable Output"""
    receipt_number = models.CharField(max_length=50, unique=True, db_index=True)
    payment_transaction = models.OneToOneField(PaymentTransaction, on_delete=models.CASCADE, related_name='receipt')

    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=30)
    customer_address = models.TextField(blank=True)

    service_name = models.CharField(max_length=200, blank=True)
    project_name = models.CharField(max_length=200, blank=True)
    payment_purpose = models.CharField(max_length=255)

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    total_paid = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")

    payment_method_name = models.CharField(max_length=100)
    gateway_name = models.CharField(max_length=100, blank=True)
    provider_transaction_id = models.CharField(max_length=255, blank=True)

    receipt_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Receipt"
        verbose_name_plural = "Payment Receipts"

    def __str__(self):
        return f"{self.receipt_number} - {self.customer_name} (₹{self.total_paid:,.2f})"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            year_str = timezone.now().strftime('%Y')
            random_num = random.randint(100000, 999999)
            self.receipt_number = f"REC-{year_str}-{random_num}"
            while PaymentReceipt.objects.filter(receipt_number=self.receipt_number).exists():
                random_num = random.randint(100000, 999999)
                self.receipt_number = f"REC-{year_str}-{random_num}"
        super().save(*args, **kwargs)


class PaymentRefund(models.Model):
    """Refund Request and Execution Management"""
    REFUND_STATUSES = [
        ('REQUESTED', 'Refund Requested'),
        ('APPROVED', 'Approved by Management'),
        ('PROCESSING', 'Processing with Gateway'),
        ('COMPLETED', 'Refund Completed'),
        ('REJECTED', 'Refund Rejected'),
    ]

    refund_reference = models.CharField(max_length=50, unique=True, db_index=True)
    payment_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name='refunds')
    requested_amount = models.DecimalField(max_digits=14, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REFUND_STATUSES, default='REQUESTED', db_index=True)
    gateway_refund_id = models.CharField(max_length=255, blank=True)

    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='requested_refunds')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_refunds')
    rejection_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Refund"
        verbose_name_plural = "Payment Refunds"

    def __str__(self):
        return f"{self.refund_reference} for {self.payment_transaction.payment_reference} (₹{self.requested_amount:,.2f}) [{self.status}]"

    def save(self, *args, **kwargs):
        if not self.refund_reference:
            year_str = timezone.now().strftime('%Y')
            random_num = random.randint(100000, 999999)
            self.refund_reference = f"REF-{year_str}-{random_num}"
            while PaymentRefund.objects.filter(refund_reference=self.refund_reference).exists():
                random_num = random.randint(100000, 999999)
                self.refund_reference = f"REF-{year_str}-{random_num}"
        super().save(*args, **kwargs)


class PaymentAuditLog(models.Model):
    """Immutable Payment Audit Trail for Complete Security & Compliance"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    payment_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    payment_request = models.ForeignKey(PaymentRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    old_status = models.CharField(max_length=40, blank=True)
    new_status = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Audit Log"
        verbose_name_plural = "Payment Audit Logs"

    def __str__(self):
        return f"Audit {self.action} @ {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
