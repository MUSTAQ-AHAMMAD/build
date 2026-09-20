from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('services/', views.service_home, name='service_home'),
    
    # Dedicated Master Service URLs (Matching Section 16 sequence)
    path('construction/', views.construction_view, name='construction'),
    path('construction-services/', views.construction_view, name='construction_services'),
    path('construction/<slug:subservice>/', views.construction_view, name='construction_sub'),

    path('renovation/', views.renovation_view, name='renovation'),
    path('flat-apartment-renovation/', views.renovation_view, name='flat_renovation'),
    path('renovation/<slug:subservice>/', views.renovation_view, name='renovation_sub'),

    path('demolition-reconstruction/', views.demolition_view, name='demolition'),
    path('demolition-reconstruction/<slug:subservice>/', views.demolition_view, name='demolition_sub'),

    path('redevelopment/', views.redevelopment_view, name='redevelopment'),
    path('property-redevelopment/', views.redevelopment_view, name='property_redevelopment'),
    path('redevelopment/<slug:subservice>/', views.redevelopment_view, name='redevelopment_sub'),

    path('property-land/', views.property_land_view, name='property_land'),
    path('land-property-services/', views.property_land_view, name='land_property_services'),
    path('nri-services/', views.nri_services_view, name='nri_services'),
    path('nri-property-services/', views.nri_services_view, name='nri_property_services'),

    path('property-inspection-assessment/', views.property_inspection_view, name='property_inspection'),
    path('government-approvals-compliance/', views.government_approvals_view, name='government_approvals'),
    path('property-documentation/', views.property_documentation_view, name='property_documentation'),
    path('bank-loan-finance-support/', views.finance_view, name='bank_loan_support'),
    path('construction-finance/', views.finance_view, name='finance'),
    path('legal-registration-coordination/', views.legal_coordination_view, name='legal_coordination'),
    path('repair-restoration-maintenance/', views.repair_maintenance_view, name='repair_maintenance'),
    path('interior-remodeling/', views.interior_remodeling_view, name='interior_remodeling'),
    path('project-management/', views.project_management_view, name='project_management'),

    # Category dispatch fallback
    path('documentation-assistance/', views.property_documentation_view, name='documentation'),
    path('government-policies/', views.government_approvals_view, name='government_policies'),
    path('services/<slug:category_slug>/', views.service_category_detail, name='service_category_detail'),
]
