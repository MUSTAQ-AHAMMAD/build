from django import forms
from .models import (
    PaymentRequest, PaymentGateway, UPIConfiguration,
    ServicePaymentConfiguration, ManualPaymentProof, PaymentSettings
)

class PaymentRequestForm(forms.ModelForm):
    class Meta:
        model = PaymentRequest
        fields = [
            'customer_name', 'customer_phone', 'customer_email',
            'lead', 'project', 'service', 'estimate',
            'payment_purpose', 'amount', 'tax_amount', 'discount_amount',
            'due_date', 'expiry_date', 'preferred_gateway', 'notes'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'lead': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
            'estimate': forms.Select(attrs={'class': 'form-select'}),
            'payment_purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Site Inspection Fee or 10% Advance'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'preferred_gateway': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PaymentGatewayForm(forms.ModelForm):
    class Meta:
        model = PaymentGateway
        fields = [
            'name', 'provider_name', 'gateway_type', 'description',
            'is_active', 'is_default', 'is_test_mode',
            'public_key', 'merchant_id', 'encrypted_secret_key',
            'checkout_url', 'custom_html', 'custom_css', 'custom_js',
            'documentation_url'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Razorpay Live / PhonePe'}),
            'provider_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Razorpay, Stripe, Cashfree, Custom'}),
            'gateway_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'public_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'rzp_live_xxx / pk_live_xxx'}),
            'merchant_id': forms.TextInput(attrs={'class': 'form-control'}),
            'encrypted_secret_key': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••••••••••'}, render_value=True),
            'checkout_url': forms.URLInput(attrs={'class': 'form-control'}),
            'custom_html': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 4, 'placeholder': '<!-- Paste provider HTML/Embed code here -->'}),
            'custom_css': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 3}),
            'custom_js': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 3}),
            'documentation_url': forms.URLInput(attrs={'class': 'form-control'}),
        }


class UPIConfigurationForm(forms.ModelForm):
    class Meta:
        model = UPIConfiguration
        fields = [
            'upi_id', 'merchant_name', 'display_name', 'qr_code_image',
            'bank_name', 'bank_account_number', 'bank_ifsc_code', 'bank_branch',
            'payment_instructions', 'is_active'
        ]
        widgets = {
            'upi_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'company@upi or mobile@paytm'}),
            'merchant_name': forms.TextInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_ifsc_code': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_branch': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ServicePaymentConfigForm(forms.ModelForm):
    class Meta:
        model = ServicePaymentConfiguration
        fields = [
            'payment_enabled', 'payment_type', 'fixed_amount',
            'advance_percentage', 'minimum_amount', 'allow_custom_amount',
            'consultation_fee', 'site_visit_fee', 'display_payment_button', 'gateway'
        ]
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'fixed_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'advance_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'minimum_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'site_visit_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'gateway': forms.Select(attrs={'class': 'form-select'}),
        }


class ManualProofSubmissionForm(forms.ModelForm):
    class Meta:
        model = ManualPaymentProof
        fields = ['method', 'bank_reference', 'notes', 'proof_document']
        widgets = {
            'method': forms.Select(attrs={'class': 'form-select'}),
            'bank_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UTR Number / Bank Ref / Cheque No', 'required': True}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional payment details...'}),
        }


class PaymentSettingsForm(forms.ModelForm):
    class Meta:
        model = PaymentSettings
        fields = [
            'company_name', 'company_address', 'currency', 'currency_symbol',
            'gst_enabled', 'gst_number', 'gst_percentage',
            'receipt_prefix', 'payment_request_prefix', 'is_test_mode_globally',
            'payment_terms', 'refund_policy'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'currency_symbol': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'receipt_prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_request_prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'refund_policy': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
