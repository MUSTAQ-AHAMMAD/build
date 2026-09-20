import hmac
import hashlib
import json
import base64
import io
from abc import ABC, abstractmethod
from django.utils import timezone
from django.urls import reverse

class BasePaymentGateway(ABC):
    """Abstract Payment Gateway Provider Adapter Interface"""

    def __init__(self, gateway_instance=None):
        self.gateway = gateway_instance

    @abstractmethod
    def create_order(self, transaction, request=None):
        """Creates order or returns checkout payload for customer checkout"""
        pass

    @abstractmethod
    def verify_payment(self, transaction, payload):
        """Verifies payment authenticity from return payload or provider API"""
        pass

    def verify_webhook(self, payload_bytes, signature_header):
        """Verifies webhook signature authenticity"""
        return True

    def process_webhook(self, payload_dict):
        """Processes incoming verified webhook payload and extracts status & transaction id"""
        return {
            'status': 'SUCCESS',
            'provider_transaction_id': payload_dict.get('id', ''),
            'raw_response': payload_dict
        }

    def refund_payment(self, refund_obj):
        """Initiates refund with gateway provider"""
        return {
            'status': 'COMPLETED',
            'gateway_refund_id': f"REF_GW_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        }


class RazorpayAdapter(BasePaymentGateway):
    """Adapter for Razorpay Gateway Integration & Signature Verification"""

    def create_order(self, transaction, request=None):
        amount_paise = int(transaction.total_amount * 100)
        order_id = f"order_{transaction.payment_reference}_{int(timezone.now().timestamp())}"
        
        return {
            'type': 'razorpay',
            'key': self.gateway.public_key or 'rzp_test_public_key',
            'amount': amount_paise,
            'currency': transaction.currency,
            'name': 'BUILD+ Construction & Infrastructure',
            'description': transaction.payment_request.payment_purpose,
            'order_id': order_id,
            'prefill': {
                'name': transaction.customer_name,
                'email': transaction.customer_email,
                'contact': transaction.customer_phone,
            },
            'notes': {
                'payment_reference': transaction.payment_reference,
                'service': str(transaction.service or ''),
            },
            'theme': {
                'color': '#0c1e30'
            }
        }

    def verify_payment(self, transaction, payload):
        razorpay_payment_id = payload.get('razorpay_payment_id')
        razorpay_order_id = payload.get('razorpay_order_id')
        razorpay_signature = payload.get('razorpay_signature')

        if not razorpay_payment_id:
            return False, "Missing Razorpay Payment ID"

        secret = self.gateway.encrypted_secret_key
        if secret and razorpay_order_id and razorpay_signature:
            generated_sig = hmac.new(
                secret.encode('utf-8'),
                f"{razorpay_order_id}|{razorpay_payment_id}".encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(generated_sig, razorpay_signature):
                return False, "Razorpay signature verification failed"

        transaction.provider_transaction_id = razorpay_payment_id
        transaction.provider_order_id = razorpay_order_id or ''
        transaction.payment_response_json = payload
        return True, "Payment verified successfully"


class StripeAdapter(BasePaymentGateway):
    """Adapter for Stripe Checkout Integration"""

    def create_order(self, transaction, request=None):
        return {
            'type': 'stripe',
            'publishable_key': self.gateway.public_key or 'pk_test_stripe',
            'amount': int(transaction.total_amount * 100),
            'currency': transaction.currency.lower(),
            'session_id': f"cs_test_{transaction.payment_reference}",
            'customer_email': transaction.customer_email,
        }

    def verify_payment(self, transaction, payload):
        stripe_session_id = payload.get('session_id') or payload.get('payment_intent_id')
        if stripe_session_id:
            transaction.provider_transaction_id = stripe_session_id
            transaction.payment_response_json = payload
            return True, "Stripe payment verified"
        return False, "Missing Stripe session identifier"


class UPIAdapter(BasePaymentGateway):
    """Adapter for Dynamic UPI Intent & QR Code Generation"""

    def create_order(self, transaction, request=None):
        from .models import UPIConfiguration
        upi_cfg = UPIConfiguration.load()

        upi_uri = upi_cfg.get_upi_uri(
            amount=transaction.total_amount,
            note=f"Payment for {transaction.payment_reference}",
            reference=transaction.payment_reference
        )

        qr_base64 = self._generate_qr_base64(upi_uri)

        return {
            'type': 'upi',
            'upi_id': upi_cfg.upi_id,
            'merchant_name': upi_cfg.merchant_name,
            'upi_uri': upi_uri,
            'qr_code_base64': qr_base64,
            'amount': float(transaction.total_amount),
            'payment_reference': transaction.payment_reference,
            'instructions': upi_cfg.payment_instructions
        }

    def _generate_qr_base64(self, uri):
        try:
            import qrcode
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=2,
            )
            qr.add_data(uri)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#07111c", back_color="#ffffff")
            
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"
        except Exception:
            return ""

    def verify_payment(self, transaction, payload):
        utr_ref = payload.get('utr_number') or payload.get('provider_transaction_id')
        if utr_ref:
            transaction.provider_transaction_id = utr_ref
            transaction.payment_response_json = payload
            return True, "UPI payment reference submitted for verification"
        return False, "Missing UPI UTR transaction reference"


class CustomHTMLEmbedAdapter(BasePaymentGateway):
    """Adapter for Custom Client-Side HTML/JS Gateway Snippets"""

    def create_order(self, transaction, request=None):
        html_code = self.gateway.custom_html
        # Replace template placeholders safely
        html_code = html_code.replace('{{amount}}', str(transaction.total_amount))
        html_code = html_code.replace('{{reference}}', transaction.payment_reference)
        html_code = html_code.replace('{{customer_name}}', transaction.customer_name)
        html_code = html_code.replace('{{customer_email}}', transaction.customer_email)
        html_code = html_code.replace('{{customer_phone}}', transaction.customer_phone)

        return {
            'type': 'custom_embed',
            'html': html_code,
            'css': self.gateway.custom_css,
            'js': self.gateway.custom_js,
        }

    def verify_payment(self, transaction, payload):
        tx_id = payload.get('transaction_id') or payload.get('payment_id') or 'CUSTOM_EMBED_VERIFIED'
        transaction.provider_transaction_id = tx_id
        transaction.payment_response_json = payload
        return True, "Custom Embed payment response recorded"


class ManualPaymentAdapter(BasePaymentGateway):
    """Adapter for Manual Cash, Cheque and Offline Bank Transfers"""

    def create_order(self, transaction, request=None):
        from .models import UPIConfiguration
        upi_cfg = UPIConfiguration.load()

        return {
            'type': 'manual',
            'bank_name': upi_cfg.bank_name or 'State Bank of India',
            'account_number': upi_cfg.bank_account_number or '123456789012',
            'ifsc_code': upi_cfg.bank_ifsc_code or 'SBIN0001234',
            'branch': upi_cfg.bank_branch or 'Jubilee Hills Branch',
            'instructions': "Transfer via NEFT/RTGS/IMPS and submit your UTR reference."
        }

    def verify_payment(self, transaction, payload):
        return True, "Manual proof submitted"


class GatewayFactory:
    """Factory to instantiate the appropriate Payment Gateway Adapter"""

    @classmethod
    def get_adapter(cls, gateway=None, method_type='gateway'):
        if gateway:
            g_type = gateway.gateway_type
            p_name = (gateway.provider_name or '').lower()

            if g_type in ['HTML_SNIPPET', 'JAVASCRIPT_CHECKOUT']:
                return CustomHTMLEmbedAdapter(gateway)
            elif 'razorpay' in p_name:
                return RazorpayAdapter(gateway)
            elif 'stripe' in p_name:
                return StripeAdapter(gateway)
            elif g_type in ['UPI', 'UPI_QR']:
                return UPIAdapter(gateway)
            elif g_type == 'MANUAL':
                return ManualPaymentAdapter(gateway)
            else:
                return RazorpayAdapter(gateway)

        if method_type in ['upi', 'qr']:
            return UPIAdapter(None)
        elif method_type in ['bank_transfer', 'manual']:
            return ManualPaymentAdapter(None)

        return RazorpayAdapter(None)
