from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import (
    ProjectCategory, Project, ProjectTask, ProjectDocument,
    SupportTicket, SupportTicketMessage
)

class ProjectAndPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='customer@example.com',
            email='customer@example.com',
            password='password123',
            first_name='Ramesh',
            last_name='Kumar'
        )
        self.staff_user = User.objects.create_user(
            username='engineer_rajesh',
            email='rajesh@buildplus.com',
            password='password123',
            is_staff=True
        )

        self.category = ProjectCategory.objects.create(name="Renovation", slug="renovation")
        self.project = Project.objects.create(
            title="3BHK Luxury Flat Renovation",
            slug="3bhk-luxury-flat-renovation",
            category=self.category,
            location="Jubilee Hills, Hyderabad",
            project_type="Complete Renovation",
            client_type="Private Homeowner",
            customer_user=self.customer,
            customer_name="Ramesh Kumar",
            customer_email="customer@example.com",
            customer_phone="+91 98765 43210",
            contract_amount=1500000.00,
            paid_amount=300000.00,
            progress_percentage=20,
            published=True
        )

        self.task = ProjectTask.objects.create(
            project=self.project,
            task_name="Old Plumbing & GI Pipe Replacement",
            category="plumbing_mep",
            status="IN_PROGRESS",
            priority="HIGH"
        )

    def test_project_models_and_tasks(self):
        self.assertEqual(self.project.tasks.count(), 1)
        self.assertEqual(self.project.progress_percentage, 20)
        self.assertEqual(str(self.task), f"{self.project.title} - Old Plumbing & GI Pipe Replacement [IN_PROGRESS]")

    def test_support_ticket_creation_and_messaging(self):
        ticket = SupportTicket.objects.create(
            customer_user=self.customer,
            customer_name="Ramesh Kumar",
            customer_phone="+91 98765 43210",
            customer_email="customer@example.com",
            project=self.project,
            category="project_progress",
            priority="MEDIUM",
            subject="Question regarding electrical distribution box location",
            description="Please confirm if the DB panel can be shifted by 2 feet.",
            status="OPEN"
        )
        self.assertTrue(ticket.ticket_id.startswith("TCK-"))

        msg = SupportTicketMessage.objects.create(
            ticket=ticket,
            sender_user=self.staff_user,
            sender_name="Engineer Rajesh",
            message="We will check the structural conduit feasibility on-site tomorrow.",
            is_staff_reply=True
        )
        self.assertEqual(ticket.messages.count(), 1)

    def test_customer_portal_authentication_and_dashboard(self):
        # Anonymous user blocked from portal dashboard
        resp = self.client.get('/portal/')
        self.assertIn(resp.status_code, [302, 403])

        # Login customer
        self.client.login(username='customer@example.com', password='password123')
        dash_resp = self.client.get('/portal/')
        self.assertEqual(dash_resp.status_code, 200)
        self.assertContains(dash_resp, "Ramesh")
        self.assertContains(dash_resp, "3BHK Luxury Flat Renovation")

        # Check portal subpages
        self.assertEqual(self.client.get('/portal/projects/').status_code, 200)
        self.assertEqual(self.client.get(f'/portal/projects/{self.project.slug}/').status_code, 200)
        self.assertEqual(self.client.get('/portal/estimates/').status_code, 200)
        self.assertEqual(self.client.get('/portal/proposals/').status_code, 200)
        self.assertEqual(self.client.get('/portal/payments/').status_code, 200)
        self.assertEqual(self.client.get('/portal/support/').status_code, 200)
        self.assertEqual(self.client.get('/portal/support/create/').status_code, 200)

    def test_portal_support_ticket_creation_flow(self):
        self.client.login(username='customer@example.com', password='password123')
        post_resp = self.client.post(
            '/portal/support/create/',
            data={
                'project_id': self.project.id,
                'category': 'billing_payment',
                'priority': 'HIGH',
                'subject': 'Receipt verification request',
                'description': 'Kindly provide receipt for advance payment.'
            }
        )
        self.assertEqual(post_resp.status_code, 302)
        
        ticket = SupportTicket.objects.filter(customer_user=self.customer, subject='Receipt verification request').first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.priority, 'HIGH')
