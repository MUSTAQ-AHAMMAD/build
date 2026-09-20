import os
import re
import json
from django.utils import timezone
from .models import AIChatbotSettings, AIKnowledgeItem

class AIConsultantEngine:
    """Core intelligence engine for Construction, Renovation & Property consulting."""

    SYSTEM_PROMPT = """You are the official AI Construction & Property Consultant for BUILD+.
BUILD+ is a premier civil engineering, construction, flat renovation, demolition, reconstruction, society redevelopment, and NRI property services consultancy.

CORE BEHAVIOR RULES:
1. Act as a trusted, professional, polite engineering consultant. Never be overly robotic or overly salesy.
2. Maintain strict safety boundaries:
   - NEVER guarantee exact pricing, fixed quotes, structural safety certifications, or loan approvals.
   - ALWAYS explain that pricing depends on measurements, structural age, condition, and materials.
   - Recommend an on-site structural audit or engineer inspection where appropriate.
3. Services you represent:
   - Construction (Independent homes, villas, G+ multi-floor, commercial)
   - Flat & Apartment Renovation (Old 20+ yr flats, damaged apartments, structural repairs, plumbing, waterproofing)
   - Controlled Demolition & Reconstruction (Partial/complete dismantling, debris removal, rebuilding)
   - Society & Property Redevelopment (FSI/TDR feasibility, society consensus, joint development)
   - Property & Land Services (Due diligence, boundary demarcation, condition audits)
   - NRI Property Services (Remote supervision, drone surveys, property stewardship)
   - Construction Finance (Loan documentation assistance - NOT a bank/lender)
4. Conversational Lead Qualification:
   - Gradually understand: Property type, condition, location, approximate area, budget range, timeline.
   - When appropriate, ask if they would like to request an on-site technical inspection or speak with an engineer.
"""

    @classmethod
    def generate_reply(cls, session, user_message):
        """Processes user message and returns (reply_text, quick_actions_list, extracted_data_dict)"""
        settings = AIChatbotSettings.load()
        user_msg_lower = user_message.lower().strip()

        # Update last activity
        session.last_activity_at = timezone.now()

        # Check for direct human handoff intent
        if any(w in user_msg_lower for w in ['talk to team', 'talk to human', 'human agent', 'speak to someone', 'call me', 'customer care', 'representative']):
            session.status = 'human_handoff'
            session.save(update_fields=['status', 'last_activity_at'])
            return (
                settings.human_handoff_message,
                [
                    {"label": "Call Us (+91 98765 43210)", "action": "tel:+919876543210", "type": "link"},
                    {"label": "Chat on WhatsApp", "action": "https://wa.me/919876543210", "type": "link"},
                    {"label": "Leave Project Details", "action": "request_summary", "type": "trigger"}
                ],
                {"status": "human_handoff"}
            )

        # 1. Try Gemini API first if configured
        gemini_api_key = os.getenv('GEMINI_API_KEY', '').strip()
        if gemini_api_key and gemini_api_key != 'your_gemini_api_key_here':
            try:
                reply, actions, data = cls._call_gemini_api(session, user_message, gemini_api_key)
                cls._update_session_data(session, data)
                return reply, actions, data
            except Exception as e:
                # Log and fallback to rule-based engine smoothly
                pass

        # 2. Rule-Based Intelligent Fallback Consultant Engine
        reply, actions, data = cls._rule_based_consultant(session, user_message)
        cls._update_session_data(session, data)
        return reply, actions, data

    @classmethod
    def _rule_based_consultant(cls, session, user_message):
        text = user_message.lower()
        extracted_data = {}
        actions = []

        # Extract contact information
        phone_match = re.search(r'(\+?\d[\d -]{8,14}\d)', user_message)
        if phone_match:
            extracted_data['visitor_phone'] = phone_match.group(1).replace(' ', '').replace('-', '')
        
        email_match = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', user_message)
        if email_match:
            extracted_data['visitor_email'] = email_match.group(1)

        # Extract locations
        for city in ['hyderabad', 'bangalore', 'bengaluru', 'chennai', 'mumbai', 'pune', 'delhi', 'vijayawada', 'vizag', 'jubilee hills', 'banjara hills', 'gachibowli', 'indiranagar', 'koramangala', 'whitefield']:
            if city in text:
                extracted_data['visitor_location'] = city.title()
                break

        # Extract Area
        area_match = re.search(r'(\d+[\d,]*)\s*(sq\.?ft|sqft|sft|sq\.?yds|sqyds|sqm)', text)
        if area_match:
            extracted_data['approximate_area'] = f"{area_match.group(1)} {area_match.group(2)}"

        # 0. Payment & Billing Intent
        if any(w in text for w in ['pay', 'payment', 'upi', 'qr code', 'receipt', 'bank transfer', 'neft', 'advance fee', 'site visit fee', 'billing']):
            extracted_data['detected_intent'] = 'Payment & Billing Assistance'
            reply = (
                "We support 100% secure, gateway-agnostic digital billing with instant GST receipts. "
                "You can pay site inspection fees, consultation charges, or project milestone advances via "
                "Online Gateway (Card / NetBanking), direct UPI mobile intent, or dynamic merchant QR.\n\n"
                "How would you like to proceed with your payment?"
            )
            actions = [
                {"label": "Pay Site Visit Fee", "action": "request_site_visit", "type": "trigger"},
                {"label": "Direct UPI & QR Guide", "action": "send_msg:How does UPI payment work?", "type": "quick_reply"},
                {"label": "Request Milestone Payment Link", "action": "request_human", "type": "trigger"},
                {"label": "Check Payment Receipt", "action": "send_msg:I need my payment receipt", "type": "quick_reply"}
            ]

        # 1. Flat & Apartment Renovation
        elif any(w in text for w in ['renovate', 'renovation', 'flat', 'apartment', 'resale', 'seepage', 'waterproofing', 'plumbing', 'bathroom', 'kitchen', 'tiles', 'interior']):
            extracted_data['service_category'] = 'renovation'
            extracted_data['service_type'] = 'flat_renovation'
            extracted_data['detected_intent'] = 'Flat & Apartment Renovation'
            
            if 'damaged' in text or 'old' in text or 'crack' in text:
                extracted_data['property_condition'] = 'Damaged / Old'
                reply = (
                    "Renovating older resale apartments (especially 15–25+ years old) often requires replacing aging GI plumbing pipes, "
                    "re-waterproofing sunken slabs, and upgrading electrical distribution boards before cosmetic work.\n\n"
                    "What is the approximate size or BHK of your flat, and which city is it in?"
                )
                actions = [
                    {"label": "2 BHK Flat (~1,200 sq.ft)", "action": "send_msg:2 BHK flat around 1200 sq.ft in Hyderabad", "type": "quick_reply"},
                    {"label": "3 BHK Flat (~1,800 sq.ft)", "action": "send_msg:3 BHK flat around 1800 sq.ft in Bangalore", "type": "quick_reply"},
                    {"label": "Complete Overhaul", "action": "send_msg:Need complete structural & interior renovation", "type": "quick_reply"},
                    {"label": "Request Site Inspection", "action": "request_site_visit", "type": "trigger"}
                ]
            else:
                reply = (
                    "We provide turnkey flat and apartment renovation—ranging from complete interior rehabilitation to structural waterproofing, "
                    "modular kitchens, and plumbing overhauls.\n\n"
                    "How would you describe the current condition of the property?"
                )
                actions = [
                    {"label": "Old Resale Flat", "action": "send_msg:It is an old resale flat needing modernization", "type": "quick_reply"},
                    {"label": "Damaged / Seepage Issues", "action": "send_msg:Property has active dampness and plumbing leaks", "type": "quick_reply"},
                    {"label": "Partial Renovation", "action": "send_msg:Only kitchen and bathroom renovation", "type": "quick_reply"},
                    {"label": "Book On-Site Visit", "action": "request_site_visit", "type": "trigger"}
                ]

        # 2. Construction
        elif any(w in text for w in ['construct', 'construction', 'new house', 'villa', 'build', 'commercial building', 'multi-floor', 'g+']):
            extracted_data['service_category'] = 'construction'
            extracted_data['service_type'] = 'residential_construction'
            extracted_data['detected_intent'] = 'New Construction'
            reply = (
                "We provide turnkey residential and commercial construction with milestone-based engineering supervision, "
                "itemized BOQ pricing, and zero hidden costs.\n\n"
                "What type of construction are you planning?"
            )
            actions = [
                {"label": "Independent House / Villa", "action": "send_msg:Independent villa construction", "type": "quick_reply"},
                {"label": "G+1 / G+2 Multi-Floor", "action": "send_msg:Multi-floor G+2 building construction", "type": "quick_reply"},
                {"label": "Commercial Building", "action": "send_msg:Commercial building project", "type": "quick_reply"},
                {"label": "Get Cost Estimate", "action": "request_estimate", "type": "trigger"}
            ]

        # 3. Demolition & Reconstruction
        elif any(w in text for w in ['demolish', 'demolition', 'dismantle', 'tear down', 'debris', 'reconstruct', 'rebuild']):
            extracted_data['service_category'] = 'demolition'
            extracted_data['service_type'] = 'building_demolition'
            extracted_data['detected_intent'] = 'Controlled Demolition & Reconstruction'
            reply = (
                "We handle controlled mechanical demolition, municipal permits, utility disconnection clearances, "
                "site waste clearance, and post-demolition structural reconstruction.\n\n"
                "Is it a full building demolition, or partial internal flat demolition?"
            )
            actions = [
                {"label": "Entire Old Building Demolition", "action": "send_msg:Full old building demolition and rebuilding", "type": "quick_reply"},
                {"label": "Internal Flat Demolition", "action": "send_msg:Internal partition wall and floor dismantling", "type": "quick_reply"},
                {"label": "Demolish & Rebuild", "action": "send_msg:Need demolition followed by new construction", "type": "quick_reply"},
                {"label": "Request Demolition Survey", "action": "request_site_visit", "type": "trigger"}
            ]

        # 4. Redevelopment
        elif any(w in text for w in ['redevelop', 'redevelopment', 'society', 'builder share', 'fsi', 'tdr']):
            extracted_data['service_category'] = 'redevelopment'
            extracted_data['service_type'] = 'property_redevelopment'
            extracted_data['detected_intent'] = 'Society & Property Redevelopment'
            reply = (
                "Our redevelopment advisory supports housing societies and property owners with structural feasibility audits, "
                "FSI/FAR optimization, legal consensus frameworks, and turnkey project management.\n\n"
                "Are you inquiring on behalf of an apartment society committee or an individual property owner?"
            )
            actions = [
                {"label": "Housing Society Committee", "action": "send_msg:Representing an apartment housing society committee", "type": "quick_reply"},
                {"label": "Individual Property Owner", "action": "send_msg:Individual landowner looking for joint development", "type": "quick_reply"},
                {"label": "Redevelopment Feasibility Check", "action": "request_site_visit", "type": "trigger"}
            ]

        # 5. NRI Services
        elif any(w in text for w in ['nri', 'abroad', 'overseas', 'remote', 'supervision', 'drone inspection', 'usa', 'gulf', 'dubai']):
            extracted_data['service_category'] = 'nri_services'
            extracted_data['service_type'] = 'nri_property_management'
            extracted_data['is_nri'] = True
            extracted_data['detected_intent'] = 'NRI Property Stewardship'
            reply = (
                "For property owners residing overseas, our senior chartered engineers provide independent third-party site audits, "
                "quarterly 4K drone surveys, remote renovation oversight, and legal boundary protection.\n\n"
                "Where is your property situated in India?"
            )
            actions = [
                {"label": "Remote Construction Supervision", "action": "send_msg:Need remote construction audit for NRI property", "type": "quick_reply"},
                {"label": "Property Inspection & Drone Audit", "action": "send_msg:Need on-site inspection and boundary audit", "type": "quick_reply"},
                {"label": "Schedule Consultation", "action": "request_site_visit", "type": "trigger"}
            ]

        # 6. Pricing & Estimates
        elif any(w in text for w in ['cost', 'price', 'pricing', 'rate', 'budget', 'estimate', 'how much', 'quote']):
            reply = (
                "Construction and renovation costs depend on carpet area, existing plumbing/electrical condition, material grades, "
                "and structural scope. We execute projects exclusively on a transparent, line-by-line Bill of Quantities (BOQ).\n\n"
                "Would you like to share your approximate property size so our engineering desk can prepare a customized estimate?"
            )
            actions = [
                {"label": "Share Property Specs", "action": "request_summary", "type": "trigger"},
                {"label": "Book Free Site Inspection", "action": "request_site_visit", "type": "trigger"},
                {"label": "Talk to Engineer", "action": "send_msg:I want to discuss pricing with an engineer", "type": "quick_reply"}
            ]

        # 7. Greeting or General
        else:
            reply = (
                "Hello! I can guide you on your construction, flat renovation, building demolition, redevelopment, or NRI property requirements.\n\n"
                "What are you currently planning?"
            )
            actions = [
                {"label": "🔨 Renovate a Flat / Apartment", "action": "send_msg:I want to renovate my flat", "type": "quick_reply"},
                {"label": "🏗️ Build a New Property", "action": "send_msg:I am planning a new construction project", "type": "quick_reply"},
                {"label": "⚡ Demolition & Reconstruction", "action": "send_msg:Need building demolition and rebuilding", "type": "quick_reply"},
                {"label": "🏢 Society Redevelopment", "action": "send_msg:Inquiring about society redevelopment", "type": "quick_reply"},
                {"label": "✈️ NRI Property Services", "action": "send_msg:I am an NRI looking for property management", "type": "quick_reply"}
            ]

        return reply, actions, extracted_data

    @classmethod
    def _call_gemini_api(cls, session, user_message, api_key):
        """Calls Google Gemini API with system instructions and chat history context"""
        from google import genai
        client = genai.Client(api_key=api_key)

        # Retrieve knowledge items for grounded context
        knowledge_snippets = AIKnowledgeItem.objects.filter(is_active=True)[:10]
        knowledge_text = "\n".join([f"- [{k.category}] {k.topic}: {k.approved_content}" for k in knowledge_snippets])

        # Prepare system prompt with live session context
        session_context = f"""
CURRENT VISITOR SESSION DATA:
- Name: {session.visitor_name or 'Unknown'}
- Location: {session.visitor_location or 'Unknown'}
- Service Category: {session.service_category or 'Unknown'}
- Property Type: {session.property_type or 'Unknown'}
- Property Condition: {session.property_condition or 'Unknown'}
- Area: {session.approximate_area or 'Unknown'}
- Is NRI: {session.is_nri}

APPROVED COMPANY KNOWLEDGE:
{knowledge_text}
"""

        prompt = f"{cls.SYSTEM_PROMPT}\n\n{session_context}\n\nVisitor Message: {user_message}\n\nProvide a helpful, concise answer (2-4 sentences max) followed by JSON format for quick actions if applicable."

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        reply_text = response.text.strip() if response.text else "I am here to assist with your construction and property requirements."
        
        # Default smart actions
        actions = [
            {"label": "Request Site Inspection", "action": "request_site_visit", "type": "trigger"},
            {"label": "Get Cost Estimate", "action": "request_estimate", "type": "trigger"},
            {"label": "Talk to Our Team", "action": "send_msg:Talk to our team", "type": "quick_reply"}
        ]

        # Extract data from rule heuristics on user_message
        _, _, extracted_data = cls._rule_based_consultant(session, user_message)

        return reply_text, actions, extracted_data

    @classmethod
    def _update_session_data(cls, session, data):
        """Merges newly extracted data into ChatSession model and calculates AI priority"""
        if not data:
            return

        fields_to_update = []
        for key, value in data.items():
            if hasattr(session, key) and value:
                setattr(session, key, value)
                fields_to_update.append(key)

        # Generate AI Lead Summary
        summary_parts = []
        if session.visitor_name:
            summary_parts.append(f"Customer: {session.visitor_name}")
        if session.service_category:
            summary_parts.append(f"Service: {session.service_category.replace('_', ' ').title()}")
        if session.property_type:
            summary_parts.append(f"Property: {session.property_type}")
        if session.visitor_location:
            summary_parts.append(f"Location: {session.visitor_location}")
        if session.approximate_area:
            summary_parts.append(f"Area: {session.approximate_area}")
        if session.site_visit_requested:
            summary_parts.append("Site Visit Requested: YES")

        if summary_parts:
            session.ai_lead_summary = " • ".join(summary_parts)
            fields_to_update.append('ai_lead_summary')

        # Calculate Priority
        if session.site_visit_requested or session.timeline in ['Immediately', 'Within 1 month']:
            session.suggested_priority = 'URGENT' if session.visitor_phone else 'HIGH'
            fields_to_update.append('suggested_priority')
        elif session.service_category in ['redevelopment', 'demolition']:
            session.suggested_priority = 'HIGH'
            fields_to_update.append('suggested_priority')

        if fields_to_update:
            session.save(update_fields=list(set(fields_to_update + ['last_activity_at'])))
