from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from crm.models import Lead, LeadSource, FollowUp, SiteVisit, Estimate, LeadNote, LeadActivity

class Command(BaseCommand):
    help = 'Seeds initial CRM lead sources, staff users, and multi-service leads'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding BUILD+ CRM module...")

        # 1. Staff Users & Roles
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True, 'first_name': 'Admin', 'last_name': 'Director'}
        )
        sales_user, _ = User.objects.get_or_create(
            username='rajesh_sales',
            defaults={'is_staff': True, 'first_name': 'Rajesh', 'last_name': 'Kumar', 'email': 'rajesh@buildplus.com'}
        )
        if not sales_user.password:
            sales_user.set_password('sales123')
            sales_user.save()

        engineer_user, _ = User.objects.get_or_create(
            username='vikram_engineer',
            defaults={'is_staff': True, 'first_name': 'Vikram', 'last_name': 'Reddy', 'email': 'vikram@buildplus.com'}
        )
        if not engineer_user.password:
            engineer_user.set_password('engineer123')
            engineer_user.save()

        # 2. Lead Sources
        sources = [
            'Website Contact Form',
            'WhatsApp Desk',
            'Direct Phone Call',
            'Google Search',
            'Google Ads',
            'Instagram / Social',
            'NRI Overseas Referral',
            'Architect Referral',
            'Existing Client',
            'Walk-in Office',
        ]
        source_objs = {}
        for s in sources:
            obj, _ = LeadSource.objects.get_or_create(name=s)
            source_objs[s] = obj

        # 3. Seed Realistic Leads Across Services
        now = timezone.now()
        today = now.date()

        leads_data = [
            {
                'first_name': 'Suresh',
                'last_name': 'Menon',
                'company_name': 'Menon Logistics',
                'phone': '+91 98490 11223',
                'email': 'suresh.menon@example.com',
                'customer_type': 'property_owner',
                'service_category': 'renovation',
                'service_type': 'flat_renovation',
                'property_type': 'flat',
                'city': 'Hyderabad',
                'area_locality': 'Banjara Hills, Road No 12',
                'property_location': 'Flat 402, Green Meadows Apts',
                'approximate_property_area': '2,400',
                'unit': 'sq.ft',
                'project_description': 'Complete overhaul of 22-year-old 3BHK flat. Replacing galvanized plumbing, upgrading electrical load for 4 ACs, designer false ceilings, and PU waterproof coatings in 3 bathrooms.',
                'estimated_budget': '₹28 - 35 Lakhs',
                'expected_project_value': 3200000.00,
                'lead_source': source_objs['Website Contact Form'],
                'assigned_to': sales_user,
                'priority': 'HIGH',
                'status': 'PROPOSAL_SENT',
                'next_follow_up_date': now + timedelta(days=1, hours=2),
            },
            {
                'first_name': 'Dr. K. V.',
                'last_name': 'Rao',
                'company_name': '',
                'phone': '+91 98850 44556',
                'email': 'dr.rao@example.com',
                'customer_type': 'property_owner',
                'service_category': 'construction',
                'service_type': 'villa_construction',
                'property_type': 'villa',
                'city': 'Hyderabad',
                'area_locality': 'Jubilee Hills, Phase 3',
                'property_location': 'Plot 142, Jubilee Hills',
                'approximate_property_area': '5,800',
                'unit': 'sq.ft',
                'project_description': 'Turnkey G+2 luxury contemporary villa on a 450 sq.yd corner plot with double-height foyer, cantilevered balconies, and solar rooftop integration.',
                'estimated_budget': '₹1.8 - 2.2 Crores',
                'expected_project_value': 19500000.00,
                'final_project_value': 19500000.00,
                'won_date': today - timedelta(days=3),
                'lead_source': source_objs['Architect Referral'],
                'assigned_to': admin_user,
                'priority': 'URGENT',
                'status': 'WON',
            },
            {
                'first_name': 'Sunil',
                'last_name': 'Agarwal',
                'company_name': 'Agarwal Real Estate Ventures',
                'phone': '+91 97000 88990',
                'email': 'sunil.agarwal@example.com',
                'customer_type': 'developer',
                'service_category': 'demolition',
                'service_type': 'building_demolition',
                'property_type': 'commercial_building',
                'city': 'Hyderabad',
                'area_locality': 'Secunderabad, MG Road',
                'property_location': 'Old Commercial Arcade, MG Road',
                'approximate_property_area': '12,000',
                'unit': 'sq.ft',
                'project_description': 'Controlled mechanical demolition of obsolete 3-story commercial complex with adjacent structures on both boundaries. Requires noise curtains and dust mist cannons.',
                'estimated_budget': '₹15 - 18 Lakhs',
                'expected_project_value': 1650000.00,
                'lead_source': source_objs['Direct Phone Call'],
                'assigned_to': engineer_user,
                'priority': 'HIGH',
                'status': 'SITE_VISIT',
                'next_follow_up_date': now + timedelta(days=2),
            },
            {
                'first_name': 'Ananya',
                'last_name': 'Deshmukh',
                'company_name': 'Shri Sai Cooperative Housing Society',
                'phone': '+91 99887 66554',
                'email': 'ananya.deshmukh@example.com',
                'customer_type': 'property_owner',
                'service_category': 'redevelopment',
                'service_type': 'apartment_redevelopment',
                'property_type': 'apartment',
                'city': 'Hyderabad',
                'area_locality': 'Himayatnagar',
                'property_location': 'Shri Sai Apts, Street No 5',
                'approximate_property_area': '18,500',
                'unit': 'sq.ft',
                'project_description': 'Housing society with 12 existing flat owners seeking joint redevelopment feasibility study. Existing structure is 34 years old.',
                'estimated_budget': '₹5.5 - 7.0 Crores',
                'expected_project_value': 62000000.00,
                'lead_source': source_objs['Website Contact Form'],
                'assigned_to': admin_user,
                'priority': 'URGENT',
                'status': 'QUALIFIED',
                'next_follow_up_date': now + timedelta(hours=4),
            },
            {
                'first_name': 'Venkat',
                'last_name': 'Ramana',
                'company_name': '',
                'phone': '+1 408 555 0192',
                'whatsapp_number': '+14085550192',
                'email': 'venkat.ramana@california.com',
                'customer_type': 'nri',
                'service_category': 'nri_services',
                'service_type': 'nri_property_management',
                'property_type': 'land',
                'city': 'Hyderabad',
                'area_locality': 'Mokila / Shankarpally',
                'property_location': 'Sy No 84, Mokila',
                'approximate_property_area': '600',
                'unit': 'sq.yards',
                'project_description': 'NRI client residing in Bay Area, California. Requires perimeter chain-link fencing, anti-encroachment signboards, and quarterly photographic drone audits.',
                'estimated_budget': '₹1.5 - 2.5 Lakhs / yr',
                'expected_project_value': 220000.00,
                'lead_source': source_objs['NRI Overseas Referral'],
                'assigned_to': sales_user,
                'priority': 'MEDIUM',
                'status': 'CONTACTED',
                'next_follow_up_date': now + timedelta(days=1),
            },
            {
                'first_name': 'Pradeep',
                'last_name': 'Reddy',
                'company_name': '',
                'phone': '+91 94400 33221',
                'email': 'pradeep.reddy@example.com',
                'customer_type': 'individual',
                'service_category': 'finance',
                'service_type': 'construction_loan',
                'property_type': 'independent_house',
                'city': 'Hyderabad',
                'area_locality': 'Kukatpally, KPHB',
                'property_location': 'Plot 88, 4th Phase KPHB',
                'approximate_property_area': '3,200',
                'unit': 'sq.ft',
                'project_description': 'Bank loan assistance for ongoing G+2 construction. Requires chartered engineer stage-wise valuation certificate and detailed BOQ for SBI loan disbursement.',
                'estimated_budget': '₹65 Lakhs Loan',
                'expected_project_value': 75000.00,
                'lead_source': source_objs['WhatsApp Desk'],
                'assigned_to': sales_user,
                'priority': 'MEDIUM',
                'status': 'REQUIREMENT_CONFIRMED',
                'next_follow_up_date': now + timedelta(days=3),
            },
            {
                'first_name': 'Mahesh',
                'last_name': 'Goud',
                'company_name': '',
                'phone': '+91 91234 56789',
                'email': 'mahesh.goud@example.com',
                'customer_type': 'property_owner',
                'service_category': 'renovation',
                'service_type': 'damaged_flat_renovation',
                'property_type': 'flat',
                'city': 'Hyderabad',
                'area_locality': 'Somajiguda',
                'property_location': 'Flat 204, Diamond Towers',
                'approximate_property_area': '1,650',
                'unit': 'sq.ft',
                'project_description': 'Severe seepage and concrete delamination from terrace slab. Chipping decayed plaster and applying polymer-modified mortar repair with PU sealants.',
                'estimated_budget': '₹8 - 12 Lakhs',
                'expected_project_value': 950000.00,
                'lead_source': source_objs['Google Ads'],
                'assigned_to': engineer_user,
                'priority': 'HIGH',
                'status': 'NEGOTIATION',
                'next_follow_up_date': now + timedelta(days=1),
            },
            {
                'first_name': 'Rahul',
                'last_name': 'Sharma',
                'company_name': '',
                'phone': '+91 99001 12233',
                'email': 'rahul.sharma@example.com',
                'customer_type': 'individual',
                'service_category': 'construction',
                'service_type': 'residential_construction',
                'property_type': 'independent_house',
                'city': 'Hyderabad',
                'area_locality': 'Gachibowli',
                'property_location': 'Gachibowli Financial District',
                'approximate_property_area': '4,200',
                'unit': 'sq.ft',
                'project_description': 'New 4BHK house construction on 300 sq.yd plot.',
                'estimated_budget': '₹85 Lakhs',
                'expected_project_value': 8500000.00,
                'lead_source': source_objs['Website Contact Form'],
                'priority': 'MEDIUM',
                'status': 'NEW',
            }
        ]

        for item in leads_data:
            lead = Lead.objects.create(**item)

            # Log Initial Creation Activity
            LeadActivity.objects.create(
                lead=lead,
                activity_type='created',
                title='Lead Generated & Logged',
                description=f"Source: {lead.lead_source.name if lead.lead_source else 'Website'}\nService: {lead.get_service_type_display()}",
                performed_by=lead.assigned_to or admin_user
            )

            # Add sample FollowUp
            if lead.status in ['CONTACTED', 'QUALIFIED', 'SITE_VISIT', 'PROPOSAL_SENT', 'NEGOTIATION']:
                FollowUp.objects.create(
                    lead=lead,
                    follow_up_date=today + timedelta(days=1),
                    follow_up_type='phone',
                    subject=f"Follow-up regarding {lead.get_service_type_display()} requirements",
                    notes="Discussed initial scope and agreed to share itemized BOQ proposal.",
                    assigned_to=lead.assigned_to or sales_user,
                    completed=False
                )

            # Add sample SiteVisit
            if lead.status in ['SITE_VISIT', 'PROPOSAL_SENT', 'NEGOTIATION', 'WON']:
                SiteVisit.objects.create(
                    lead=lead,
                    site_address=lead.property_location or f"{lead.area_locality}, {lead.city}",
                    visit_date=today - timedelta(days=1),
                    visit_time='10:30:00',
                    assigned_staff=engineer_user,
                    site_contact=f"{lead.full_name} ({lead.phone})",
                    property_type=lead.get_property_type_display(),
                    site_condition="Structure inspected. Sound RCC frame, accessible road width for material transport.",
                    requirements=lead.project_description,
                    measurements=f"Verified area: ~{lead.approximate_property_area or '2,000'} {lead.unit}",
                    status='completed'
                )

            # Add sample Estimate
            if lead.status in ['PROPOSAL_SENT', 'NEGOTIATION', 'WON']:
                est_val = lead.expected_project_value or 2500000.00
                Estimate.objects.create(
                    lead=lead,
                    description=f"{lead.get_service_type_display()} Detailed BOQ Rev-1",
                    estimated_amount=est_val * 0.82,
                    tax_amount=est_val * 0.18,
                    total_amount=est_val,
                    status='approved' if lead.status == 'WON' else 'sent'
                )

            # Add sample Note
            LeadNote.objects.create(
                lead=lead,
                note=f"Client is very particular about high-quality material specifications and transparent milestone inspections.",
                created_by=lead.assigned_to or admin_user
            )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(leads_data)} comprehensive CRM leads with full activity timeline, follow-ups, site visits, and estimates!"))
