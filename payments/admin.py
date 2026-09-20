from django.contrib import admin
from .models import (
    PaymentSettings, PaymentGateway, PaymentMethod, UPIConfiguration,
    ServicePaymentConfiguration, PaymentRequest, PaymentTransaction,
    ProjectPaymentMilestone, ManualPaymentProof, PaymentReceipt,
    PaymentRefund, PaymentAuditLog
)

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'currency', 'gst_enabled', 'gst_number', 'is_test_mode_globally', 'updated_at']

@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider_name', 'gateway_type', 'is_active', 'is_default', 'is_test_mode', 'updated_at']
    list_filter = ['gateway_type', 'is_active', 'is_default', 'is_test_mode']
    search_fields = ['name', 'provider_name', 'public_key']

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'method_type', 'gateway', 'is_active', 'sort_order']
    list_filter = ['method_type', 'is_active']

@admin.register(UPIConfiguration)
class UPIConfigurationAdmin(admin.ModelAdmin):
    list_display = ['merchant_name', 'upi_id', 'bank_name', 'is_active', 'updated_at']

@admin.register(ServicePaymentConfiguration)
class ServicePaymentConfigAdmin(admin.ModelAdmin):
    list_display = ['service', 'payment_enabled', 'payment_type', 'fixed_amount', 'advance_percentage', 'display_payment_button']
    list_filter = ['payment_enabled', 'payment_type']

@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ['payment_reference', 'customer_name', 'customer_phone', 'total_amount', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['payment_reference', 'customer_name', 'customer_phone', 'customer_email']
    readonly_fields = ['uuid', 'payment_reference', 'created_at', 'updated_at']

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['payment_reference', 'customer_name', 'total_amount', 'status', 'gateway', 'payment_method_type', 'provider_transaction_id', 'created_at']
    list_filter = ['status', 'payment_method_type', 'is_test_mode', 'created_at']
    search_fields = ['payment_reference', 'customer_name', 'customer_phone', 'provider_transaction_id', 'provider_order_id']
    readonly_fields = ['uuid', 'payment_reference', 'initiated_at', 'created_at', 'updated_at']

@admin.register(ProjectPaymentMilestone)
class ProjectPaymentMilestoneAdmin(admin.ModelAdmin):
    list_display = ['project', 'milestone_name', 'percentage', 'amount', 'due_date', 'status']
    list_filter = ['status']
    search_fields = ['project__title', 'milestone_name']

@admin.register(ManualPaymentProof)
class ManualPaymentProofAdmin(admin.ModelAdmin):
    list_display = ['payment_reference', 'method', 'bank_reference', 'status', 'verified_by', 'verified_at', 'created_at']
    list_filter = ['status', 'method']
    search_fields = ['payment_reference', 'bank_reference']

@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'customer_name', 'total_paid', 'payment_purpose', 'receipt_date', 'created_at']
    search_fields = ['receipt_number', 'customer_name', 'customer_phone', 'provider_transaction_id']
    readonly_fields = ['receipt_number', 'created_at']

@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = ['refund_reference', 'payment_transaction', 'requested_amount', 'status', 'requested_by', 'approved_by', 'created_at']
    list_filter = ['status']
    search_fields = ['refund_reference', 'payment_transaction__payment_reference']

@admin.register(PaymentAuditLog)
class PaymentAuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'old_status', 'new_status', 'ip_address', 'created_at']
    readonly_fields = ['created_at']
