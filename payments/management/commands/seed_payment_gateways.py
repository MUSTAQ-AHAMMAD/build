from django.core.management.base import BaseCommand
from payments.models import (
    PaymentSettings, PaymentGateway, PaymentMethod, UPIConfiguration,
    ServicePaymentConfiguration
)
from services.models import Service

class Command(BaseCommand):
    help = "Seed standard payment gateways, methods, UPI configuration, and service payment pricing"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding Payment Gateway settings & configurations...")

        # 1. Payment Settings
        settings = PaymentSettings.load()
        settings.company_name = "BUILD+ Construction & Infrastructure"
        settings.currency = "INR"
        settings.currency_symbol = "₹"
        settings.gst_enabled = True
        settings.gst_number = "36AAAAA0000A1Z5"
        settings.gst_percentage = 18.00
        settings.save()

        # 2. UPI Configuration
        upi_cfg = UPIConfiguration.load()
        upi_cfg.upi_id = "buildplus@upi"
        upi_cfg.merchant_name = "BUILD+ Construction & Infrastructure"
        upi_cfg.bank_name = "HDFC Bank"
        upi_cfg.bank_account_number = "50200012345678"
        upi_cfg.bank_ifsc_code = "HDFC0000036"
        upi_cfg.bank_branch = "Jubilee Hills, Hyderabad"
        upi_cfg.is_active = True
        upi_cfg.save()

        # 3. Standard Gateways
        rzp, _ = PaymentGateway.objects.get_or_create(
            slug="razorpay-online",
            defaults={
                'name': 'Razorpay Online Gateway',
                'provider_name': 'Razorpay',
                'gateway_type': 'HOSTED_CHECKOUT',
                'description': 'Accept credit cards, debit cards, net banking, UPI, and wallets via Razorpay.',
                'is_active': True,
                'is_default': True,
                'is_test_mode': True,
                'public_key': 'rzp_test_buildplus_public',
                'encrypted_secret_key': 'rzp_test_secret_key_buildplus',
                'documentation_url': 'https://razorpay.com/docs/payments/payment-gateway/',
            }
        )

        stripe, _ = PaymentGateway.objects.get_or_create(
            slug="stripe-checkout",
            defaults={
                'name': 'Stripe Global Checkout',
                'provider_name': 'Stripe',
                'gateway_type': 'HOSTED_CHECKOUT',
                'description': 'International cards and NRI payment processing via Stripe.',
                'is_active': True,
                'is_default': False,
                'is_test_mode': True,
                'public_key': 'pk_test_buildplus_stripe',
                'documentation_url': 'https://stripe.com/docs/checkout',
            }
        )

        upi_gw, _ = PaymentGateway.objects.get_or_create(
            slug="upi-direct",
            defaults={
                'name': 'Direct UPI & Dynamic QR',
                'provider_name': 'UPI',
                'gateway_type': 'UPI',
                'description': 'Direct zero-fee mobile UPI and QR scan payments.',
                'is_active': True,
                'is_default': False,
                'is_test_mode': False,
            }
        )

        custom_gw, _ = PaymentGateway.objects.get_or_create(
            slug="custom-embed-gateway",
            defaults={
                'name': 'Custom Payment Provider Embed',
                'provider_name': 'Custom',
                'gateway_type': 'HTML_SNIPPET',
                'description': 'Administrator copy-paste client-side embed code integration.',
                'is_active': False,
                'is_default': False,
                'is_test_mode': True,
                'custom_html': '<div class="p-3 bg-light rounded text-center"><p class="mb-2 fw-semibold">Click below to proceed to external payment desk:</p><button type="button" class="btn btn-primary" onclick="alert(\'External provider script triggered for reference: {{reference}} and amount: ₹{{amount}}\');">Proceed via Embed Desk</button></div>',
            }
        )

        # 4. Customer Payment Methods
        PaymentMethod.objects.get_or_create(
            name="Online Gateway (Card / NetBanking)",
            defaults={
                'method_type': 'gateway',
                'gateway': rzp,
                'display_name': 'Credit / Debit Card & NetBanking',
                'description': 'Pay securely with Visa, MasterCard, RuPay, Amex or 50+ NetBanking banks',
                'icon': '💳',
                'sort_order': 1,
                'is_active': True,
            }
        )

        PaymentMethod.objects.get_or_create(
            name="UPI Mobile & Apps",
            defaults={
                'method_type': 'upi',
                'gateway': upi_gw,
                'display_name': 'UPI Apps (GPay, PhonePe, Paytm)',
                'description': 'Direct 1-tap mobile payment to official company VPA',
                'icon': '📱',
                'sort_order': 2,
                'is_active': True,
            }
        )

        PaymentMethod.objects.get_or_create(
            name="Scan UPI QR Code",
            defaults={
                'method_type': 'qr',
                'gateway': upi_gw,
                'display_name': 'Scan & Pay QR Code',
                'description': 'Scan dynamically generated merchant QR from any banking app',
                'icon': '⬛',
                'sort_order': 3,
                'is_active': True,
            }
        )

        PaymentMethod.objects.get_or_create(
            name="Direct Bank Transfer",
            defaults={
                'method_type': 'bank_transfer',
                'display_name': 'Bank Transfer (NEFT / RTGS / IMPS)',
                'description': 'Direct corporate RTGS/NEFT transfer with manual UTR submission',
                'icon': '🏦',
                'sort_order': 4,
                'is_active': True,
            }
        )

        # 5. Service Payment Pricing Defaults
        for s in Service.objects.all():
            cfg, created = ServicePaymentConfiguration.objects.get_or_create(service=s)
            if created or not cfg.fixed_amount:
                cat_slug = s.category.slug if s.category else ''
                if 'renovation' in cat_slug:
                    cfg.consultation_fee = 1000.00
                    cfg.site_visit_fee = 1500.00
                    cfg.fixed_amount = 1500.00
                    cfg.advance_percentage = 10.00
                elif 'construction' in cat_slug or 'reconstruction' in cat_slug:
                    cfg.consultation_fee = 1500.00
                    cfg.site_visit_fee = 2500.00
                    cfg.fixed_amount = 2500.00
                    cfg.advance_percentage = 10.00
                else:
                    cfg.consultation_fee = 1000.00
                    cfg.site_visit_fee = 2000.00
                    cfg.fixed_amount = 2000.00
                    cfg.advance_percentage = 5.00
                cfg.payment_enabled = True
                cfg.display_payment_button = True
                cfg.gateway = rzp
                cfg.save()

        self.stdout.write(self.style.SUCCESS("Successfully seeded payment gateways and service pricing configs!"))
