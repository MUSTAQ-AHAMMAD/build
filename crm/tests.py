from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from crm.models import Lead, LeadSource, FollowUp, SiteVisit, Estimate, LeadNote, LeadActivity
from crm.forms import LeadForm, LeadMarkWonForm, LeadMarkLostForm

class CRMModelTests(TestCase):
    def setUp(self):
        self.source = LeadSource.objects.create(name="Website Portal")
        self.user = User.objects.create_user(username='staff_rep', is_staff=True)

    def test_lead_id_auto_generation(self):
        lead = Lead.objects.create(
            first_name="Anand",
            last_name="Verma",
            phone="+91 98765 11111",
            service_category="renovation",
            service_type="flat_renovation",
            lead_source=self.source
        )
        self.assertTrue(lead.lead_id.startswith("LEAD-"))
        self.assertEqual(lead.full_name, "Anand Verma")
        self.assertEqual(lead.status, "NEW")
        self.assertFalse(lead.is_deleted)

    def test_estimate_auto_numbering_and_total(self):
        lead = Lead.objects.create(
            first_name="Ravi",
            phone="+91 98765 22222",
            service_category="construction",
            service_type="residential_construction"
        )
        estimate = Estimate.objects.create(
            lead=lead,
            description="3BHK Civil Work Estimate",
            estimated_amount=1000000.00,
            tax_amount=180000.00
        )
        self.assertTrue(estimate.estimate_number.startswith("EST-"))
        self.assertEqual(float(estimate.total_amount), 1180000.00)

    def test_followup_overdue_and_completion(self):
        lead = Lead.objects.create(
            first_name="Vikram",
            phone="+91 98765 33333",
            service_category="demolition",
            service_type="building_demolition",
            next_follow_up_date=timezone.now() - timedelta(days=2)
        )
        self.assertTrue(lead.is_overdue)

        fu = FollowUp.objects.create(
            lead=lead,
            follow_up_date=timezone.now().date() - timedelta(days=2),
            subject="Check permit documents",
            assigned_to=self.user
        )
        self.assertFalse(fu.completed)


class CRMViewAndWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='super_admin', password='password123', email='admin@test.com')
        self.sales_user = User.objects.create_user(username='sales_agent', password='password123', is_staff=True)
        self.regular_user = User.objects.create_user(username='regular_user', password='password123', is_staff=False)
        self.source = LeadSource.objects.create(name="Direct Phone")

        self.lead = Lead.objects.create(
            first_name="Karthik",
            last_name="Rao",
            phone="+91 98111 22222",
            email="karthik@test.com",
            service_category="renovation",
            service_type="old_flat_renovation",
            city="Hyderabad",
            area_locality="Banjara Hills",
            lead_source=self.source,
            assigned_to=self.sales_user,
            status="QUALIFIED",
            priority="HIGH",
            expected_project_value=1500000.00
        )

    def test_anonymous_access_redirects_to_login(self):
        response = self.client.get(reverse('crm:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/cms/login/', response.url)

    def test_regular_user_blocked(self):
        self.client.login(username='regular_user', password='password123')
        response = self.client.get(reverse('crm:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_staff_dashboard_renders_metrics(self):
        self.client.login(username='sales_agent', password='password123')
        response = self.client.get(reverse('crm:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sales Pipeline")
        self.assertContains(response, "Karthik Rao")

    def test_lead_list_search_and_filter(self):
        self.client.login(username='sales_agent', password='password123')
        
        # Search by name
        resp = self.client.get(reverse('crm:lead_list') + '?q=Karthik')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Karthik Rao")

        # Search non-existent
        resp_none = self.client.get(reverse('crm:lead_list') + '?q=NonExistentPerson')
        self.assertEqual(resp_none.status_code, 200)
        self.assertNotContains(resp_none, "Karthik Rao")

        # Category filter
        resp_filter = self.client.get(reverse('crm:lead_list') + '?category=renovation')
        self.assertEqual(resp_filter.status_code, 200)
        self.assertContains(resp_filter, "Karthik Rao")

    def test_lead_create_view(self):
        self.client.login(username='sales_agent', password='password123')
        response = self.client.post(reverse('crm:lead_create'), {
            'first_name': 'Meera',
            'last_name': 'Nair',
            'phone': '+91 98333 44444',
            'email': 'meera@test.com',
            'customer_type': 'individual',
            'preferred_contact_method': 'phone',
            'service_category': 'construction',
            'service_type': 'residential_construction',
            'property_type': 'independent_house',
            'city': 'Hyderabad',
            'area_locality': 'Gachibowli',
            'approximate_property_area': '3,500',
            'unit': 'sq.ft',
            'priority': 'MEDIUM',
            'status': 'NEW',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Lead.objects.filter(first_name='Meera', last_name='Nair').exists())

    def test_lead_detail_view(self):
        self.client.login(username='sales_agent', password='password123')
        response = self.client.get(reverse('crm:lead_detail', kwargs={'pk': self.lead.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lead.lead_id)
        self.assertContains(response, "Karthik Rao")

    def test_workflow_mark_won(self):
        self.client.login(username='sales_agent', password='password123')
        response = self.client.post(reverse('crm:lead_mark_won', kwargs={'pk': self.lead.pk}), {
            'final_project_value': 1450000.00,
            'won_date': timezone.now().date(),
            'won_notes': 'Contract signed with 20% advance.'
        })
        self.assertEqual(response.status_code, 302)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, 'WON')
        self.assertEqual(float(self.lead.final_project_value), 1450000.00)
        self.assertTrue(LeadActivity.objects.filter(lead=self.lead, activity_type='marked_won').exists())

    def test_workflow_mark_lost(self):
        self.client.login(username='sales_agent', password='password123')
        response = self.client.post(reverse('crm:lead_mark_lost', kwargs={'pk': self.lead.pk}), {
            'lost_reason': 'budget',
            'lost_notes': 'Client postponed due to budget allocation.'
        })
        self.assertEqual(response.status_code, 302)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, 'LOST')
        self.assertEqual(self.lead.lost_reason, 'budget')

    def test_soft_delete_and_restore(self):
        self.client.login(username='sales_agent', password='password123')
        lead_pk = self.lead.pk

        # Soft delete
        response = self.client.post(reverse('crm:lead_delete', kwargs={'pk': lead_pk}))
        self.assertEqual(response.status_code, 302)
        self.lead.refresh_from_db()
        self.assertTrue(self.lead.is_deleted)
        self.assertIsNotNone(self.lead.deleted_at)

        # Restore
        resp_restore = self.client.post(reverse('crm:lead_restore', kwargs={'pk': lead_pk}))
        self.assertEqual(resp_restore.status_code, 302)
        self.lead.refresh_from_db()
        self.assertFalse(self.lead.is_deleted)

    def test_followup_complete_action(self):
        self.client.login(username='sales_agent', password='password123')
        fu = FollowUp.objects.create(
            lead=self.lead,
            follow_up_date=timezone.now().date(),
            subject="Clarify structural drawings",
            assigned_to=self.sales_user
        )
        response = self.client.post(reverse('crm:followup_complete', kwargs={'pk': fu.pk}), {
            'outcome': 'Client approved drawings.'
        })
        self.assertEqual(response.status_code, 302)
        fu.refresh_from_db()
        self.assertTrue(fu.completed)
        self.assertEqual(fu.outcome, 'Client approved drawings.')

    def test_crm_reports_view(self):
        self.client.login(username='sales_agent', password='password123')
        response = self.client.get(reverse('crm:reports'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conversion")
        self.assertContains(response, "Service Category")

    def test_public_website_enquiry_auto_syncs_to_crm(self):
        # Visitor fills public contact form
        response = self.client.post('/contact/', {
            'enquiry_type': 'flat_renovation',
            'full_name': 'Govind Narayan',
            'phone_number': '+91 97777 88888',
            'email': 'govind@example.com',
            'city_location': 'Madhapur, Hyderabad',
            'property_type': '3BHK Resale Flat',
            'approximate_area': '2,100 sq.ft',
            'message': 'Need complete plumbing and electrical overhaul.',
            'site_visit_requested': True,
        })
        self.assertEqual(response.status_code, 302)

        # Verify CRM Lead was automatically created
        crm_lead = Lead.objects.filter(phone='+91 97777 88888').first()
        self.assertIsNotNone(crm_lead)
        self.assertEqual(crm_lead.first_name, 'Govind')
        self.assertEqual(crm_lead.last_name, 'Narayan')
        self.assertEqual(crm_lead.service_category, 'renovation')
        self.assertEqual(crm_lead.service_type, 'flat_renovation')
        self.assertEqual(crm_lead.status, 'SITE_VISIT')
        self.assertTrue(crm_lead.lead_id.startswith('LEAD-'))
        
        # Verify SiteVisit record was auto-scheduled
        self.assertTrue(SiteVisit.objects.filter(lead=crm_lead).exists())
        # Verify LeadActivity was created
        self.assertTrue(LeadActivity.objects.filter(lead=crm_lead, activity_type='created').exists())
