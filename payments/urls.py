from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Public Secure Payment Pages
    path('pay/<uuid:token>/', views.public_payment_page, name='public_pay'),
    path('pay/<uuid:token>/checkout/', views.public_initiate_checkout, name='public_checkout'),
    path('pay/<uuid:token>/verify/', views.public_verify_payment, name='public_verify'),
    path('pay/<uuid:token>/manual-submit/', views.public_manual_proof_submit, name='public_manual_submit'),
    path('pay/<uuid:token>/success/', views.public_payment_success, name='public_success'),
    path('pay/<uuid:token>/failed/', views.public_payment_failed, name='public_failed'),
    path('pay/<uuid:token>/pending/', views.public_payment_pending, name='public_pending'),
    path('pay/receipt/<str:receipt_number>/', views.public_view_receipt, name='public_receipt'),

    # Webhooks
    path('payments/webhook/<slug:gateway_slug>/', views.payment_webhook_handler, name='webhook_handler'),

    # Payment Workspace Root & Aliases
    path('payment/', views.cms_payment_dashboard, name='workspace_root'),
    path('payment/dashboard/', views.cms_payment_dashboard, name='workspace_dashboard'),
    path('payment/transactions/', views.cms_transaction_list, name='workspace_transactions'),
    path('payment/requests/', views.cms_payment_requests, name='workspace_requests'),
    path('payment/requests/create/', views.cms_payment_request_create, name='workspace_request_create'),
    path('payment/manual-verification/', views.cms_manual_verification_desk, name='workspace_manual_verification'),
    path('payment/refunds/', views.cms_refunds_manager, name='workspace_refunds'),
    path('payment/gateways/', views.cms_gateways_list, name='workspace_gateways'),
    path('payment/upi/', views.cms_upi_config, name='workspace_upi'),
    path('payment/settings/', views.cms_payment_settings, name='workspace_settings'),

    # CMS Payment Hub & Management (Backward compatibility)
    path('cms/payments/', views.cms_payment_dashboard, name='cms_dashboard'),
    path('cms/payments/dashboard/', views.cms_payment_dashboard, name='cms_dashboard_alias'),
    path('cms/payments/transactions/', views.cms_transaction_list, name='cms_transactions'),
    path('cms/payments/requests/', views.cms_payment_requests, name='cms_requests'),
    path('cms/payments/requests/create/', views.cms_payment_request_create, name='cms_request_create'),
    path('cms/payments/manual-verification/', views.cms_manual_verification_desk, name='cms_manual_verification'),
    path('cms/payments/refunds/', views.cms_refunds_manager, name='cms_refunds'),
    path('cms/payments/gateways/', views.cms_gateways_list, name='cms_gateways'),
    path('cms/payments/gateways/create/', views.cms_gateway_edit, name='cms_gateway_create'),
    path('cms/payments/gateways/<int:gateway_id>/edit/', views.cms_gateway_edit, name='cms_gateway_edit'),
    path('cms/payments/upi/', views.cms_upi_config, name='cms_upi'),
    path('cms/payments/services-pricing/', views.cms_service_pricing, name='cms_service_pricing'),
    path('cms/payments/settings/', views.cms_payment_settings, name='cms_settings'),
]
