from django.test import TestCase, Client
from django.urls import reverse
from enquiries.models import Enquiry
from core.models import WebsiteSettings, FAQ, Testimonial

class CoreAndEnquiryPortalTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_renders_ok(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Build Better")
        self.assertContains(response, "Flat & Apartment Renovation")

    def test_services_pages_render_ok(self):
        endpoints = [
            '/construction/',
            '/renovation/',
            '/demolition-reconstruction/',
            '/redevelopment/',
            '/property-land/',
            '/nri-services/',
            '/construction-finance/',
            '/about/',
            '/how-we-work/',
            '/faqs/',
        ]
        for url in endpoints:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"URL {url} failed to return 200")

    def test_public_enquiry_submission(self):
        response = self.client.post('/contact/', {
            'enquiry_type': 'flat_renovation',
            'full_name': 'Ramesh Sharma',
            'phone_number': '+91 98765 00000',
            'email': 'ramesh@example.com',
            'city_location': 'Banjara Hills, Hyderabad',
            'property_type': '3BHK Resale Flat',
            'approximate_area': '1,950 sq.ft',
            'message': 'Need complete plumbing and bathroom renovation.',
            'site_visit_requested': True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Enquiry.objects.filter(full_name='Ramesh Sharma').exists())
        enquiry = Enquiry.objects.get(full_name='Ramesh Sharma')
        self.assertEqual(enquiry.status, 'NEW')
        self.assertEqual(enquiry.enquiry_type, 'flat_renovation')
