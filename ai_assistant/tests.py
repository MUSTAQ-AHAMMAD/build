import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage, AIChatbotSettings, AIKnowledgeItem
from crm.models import Lead, SiteVisit, LeadActivity

class AIAssistantPublicAndCRMTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='ai_staff', email='ai_staff@example.com', password='password123', is_staff=True
        )
        self.settings = AIChatbotSettings.load()
        self.settings.is_enabled = True
        self.settings.ai_name = "BUILD+ AI Consultant"
        self.settings.save()

    def test_ai_init_endpoint(self):
        resp = self.client.get('/api/ai/init/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue('session_id' in data)
        self.assertTrue(len(data['messages']) >= 1)

    def test_ai_chat_renovation_intent_and_reply(self):
        # 1. Initialize session
        init_resp = self.client.get('/api/ai/init/')
        session_id = init_resp.json()['session_id']

        # 2. Post user message
        payload = {
            'session_id': session_id,
            'message': 'I have an old 3BHK flat in Jubilee Hills Hyderabad with bathroom seepage and need full renovation.'
        }
        resp = self.client.post(
            '/api/ai/message/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('reply', data)
        self.assertTrue(len(data['reply']['quick_actions']) > 0)
        
        # Verify Session Data Extraction
        session = ChatSession.objects.get(session_id=session_id)
        self.assertEqual(session.service_category, 'renovation')
        self.assertEqual(session.visitor_location, 'Hyderabad')

    def test_ai_chat_human_takeover_intent(self):
        init_resp = self.client.get('/api/ai/init/')
        session_id = init_resp.json()['session_id']

        payload = {
            'session_id': session_id,
            'message': 'I want to talk to human customer care staff.'
        }
        resp = self.client.post(
            '/api/ai/message/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        session = ChatSession.objects.get(session_id=session_id)
        self.assertEqual(session.status, 'human_handoff')

    def test_ai_lead_capture_creates_crm_lead(self):
        init_resp = self.client.get('/api/ai/init/')
        session_id = init_resp.json()['session_id']

        payload = {
            'session_id': session_id,
            'name': 'Meera Sundaram',
            'phone': '+91 99000 11223',
            'email': 'meera.s@example.com',
            'location': 'Indiranagar, Bangalore',
            'service_category': 'renovation',
            'service_type': 'flat_renovation',
            'property_type': '3BHK Apartment',
            'approximate_area': '1,650 sq.ft',
            'budget': '₹25–50 Lakhs',
            'timeline': 'Immediately',
            'site_visit_requested': True,
        }
        resp = self.client.post(
            '/api/ai/lead-capture/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue(data['lead_id'].startswith('LEAD-'))

        # Verify CRM Lead created
        lead = Lead.objects.filter(phone='+91 99000 11223').first()
        self.assertIsNotNone(lead)
        self.assertEqual(lead.lead_source.name, 'AI Chatbot')
        self.assertEqual(lead.status, 'SITE_VISIT')

        # Verify Site Visit booked
        sv = SiteVisit.objects.filter(lead=lead).first()
        self.assertIsNotNone(sv)

        # Verify LeadActivity audit
        act = LeadActivity.objects.filter(lead=lead).first()
        self.assertIsNotNone(act)

    def test_cms_ai_dashboard_and_permission_gating(self):
        # Anonymous blocked
        anon_resp = self.client.get('/cms/ai/')
        self.assertIn(anon_resp.status_code, [302, 403])

        # Staff allowed
        self.client.force_login(self.staff_user)
        staff_resp = self.client.get('/cms/ai/')
        self.assertEqual(staff_resp.status_code, 200)
        self.assertContains(staff_resp, "AI Customer Assistant")

        conv_resp = self.client.get('/cms/ai/conversations/')
        self.assertEqual(conv_resp.status_code, 200)

        sett_resp = self.client.get('/cms/ai/settings/')
        self.assertEqual(sett_resp.status_code, 200)

        know_resp = self.client.get('/cms/ai/knowledge/')
        self.assertEqual(know_resp.status_code, 200)

    def test_cms_human_takeover_and_reply(self):
        init_resp = self.client.get('/api/ai/init/')
        session_id = init_resp.json()['session_id']

        self.client.force_login(self.staff_user)
        
        # Toggle human takeover
        resp = self.client.post(
            f'/cms/ai/conversations/{session_id}/',
            data={'action': 'toggle_takeover'}
        )
        self.assertEqual(resp.status_code, 302)
        session = ChatSession.objects.get(session_id=session_id)
        self.assertTrue(session.human_agent_active)

        # Send manual staff reply
        resp_reply = self.client.post(
            f'/cms/ai/conversations/{session_id}/',
            data={'action': 'send_manual_reply', 'manual_reply': 'Hello Meera! I am reviewing your floor plan now.'}
        )
        self.assertEqual(resp_reply.status_code, 302)

        last_msg = session.messages.last()
        self.assertEqual(last_msg.sender_type, 'human_agent')
        self.assertIn("reviewing your floor plan", last_msg.content)
