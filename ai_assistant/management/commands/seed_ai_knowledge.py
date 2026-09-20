from django.core.management.base import BaseCommand
from ai_assistant.models import AIChatbotSettings, AIKnowledgeItem

class Command(BaseCommand):
    help = 'Seeds initial AI knowledge base and settings for BUILD+ AI Assistant'

    def handle(self, *args, **options):
        # 1. Initialize Settings
        settings = AIChatbotSettings.load()
        settings.ai_name = "BUILD+ AI Consultant"
        settings.is_enabled = True
        settings.save()
        self.stdout.write(self.style.SUCCESS("[OK] AI Chatbot settings verified."))

        # 2. Seed Knowledge Items
        items = [
            {
                'category': 'renovation',
                'topic': 'Resale Flat Renovation (15-25+ Years Old)',
                'keywords': 'resale flat, old apartment, plumbing, gi pipes, seepage, bathroom leak, floor tiles',
                'approved_content': 'Older apartments built prior to 2010 typically suffer from rusted GI internal piping, degraded sunken slab waterproofing in washrooms, and undersized electrical distribution. Our turnkey renovation replaces internal plumbing with CPVC/UPVC, strips and re-waterproofs bathrooms with multi-coat polymer elastomeric barriers, and updates concealed copper wiring with modern RCBO safety breakers.',
                'who_is_it_for': 'Owners and buyers of aging apartments and resale flats.',
                'typical_process': '1. Civil & plumbing audit -> 2. Non-structural strip-down -> 3. Core plumbing & waterproofing -> 4. Electrical & false ceiling -> 5. Premium finishes & sanitization.',
                'pricing_guideline': 'Determined by carpet area, extent of plumbing replacement, and material selection (Standard / Premium / Luxury).',
                'safety_boundary': 'Structural load-bearing columns and shear walls are strictly preserved. Modifying RCC beams is prohibited.'
            },
            {
                'category': 'construction',
                'topic': 'Turnkey Residential Villa & Custom House Construction',
                'keywords': 'villa, independent house, duplex, g+1, g+2, custom home, turnkey construction',
                'approved_content': 'We execute turnkey residential construction from soil testing and architectural floor plans to structural RCC framing, brick masonry, plastering, premium flooring, and municipal occupancy certificates. All projects operate on transparent itemized Bill of Quantities (BOQ) with scheduled milestone stage payments.',
                'who_is_it_for': 'Plot owners planning independent houses, villas, or multi-family residences.',
                'typical_process': '1. Soil test & structural design -> 2. Municipal sanctions -> 3. Plinth & RCC superstructure -> 4. Masonry & MEP rough-in -> 5. Turnkey interior & exterior handover.',
                'pricing_guideline': 'Priced per sq.ft built-up area based on chosen finish specifications (Standard, Premium, Ultra-Luxury).',
                'safety_boundary': 'All structural RCC detailing conforms to IS 456 and seismic zone safety requirements.'
            },
            {
                'category': 'demolition',
                'topic': 'Controlled Mechanical Demolition & Structural Dismantling',
                'keywords': 'demolish, demolition, dismantling, mechanical demolition, debris removal, old building, safety mesh',
                'approved_content': 'Controlled mechanical demolition utilizes specialized hydraulic shears, diamond wire sawing, and protective containment netting. We manage municipal demolition permits, utility gas/power/water disconnections, dust suppression systems, and authorized green debris disposal.',
                'who_is_it_for': 'Property owners, builders, and developers with distressed, dilapidated, or encroaching structures.',
                'typical_process': '1. Structural neighbor impact survey -> 2. Utility isolations & permit clearance -> 3. Protective scaffolding & dust netting -> 4. Top-down mechanical dismantling -> 5. Site excavation & debris clearance.',
                'pricing_guideline': 'Priced based on structural volume (cubic meters), RCC density, accessibility, and salvageable metal credit.',
                'safety_boundary': 'Never execute uncontained manual tumbling. Continuous vibration monitoring on adjacent buildings is mandatory.'
            },
            {
                'category': 'redevelopment',
                'topic': 'Housing Society & Property Redevelopment',
                'keywords': 'society redevelopment, apartment redevelopment, fsi, tdr, joint development, builder share',
                'approved_content': 'We provide end-to-end technical, legal, and project management advisory for housing society redevelopment. We conduct structural audit certification, maximize permissible FSI/TDR utilization under current master plans, draft transparent tender documentation, and supervise the rebuild until handover.',
                'who_is_it_for': 'Apartment Owner Associations (RWA), cooperative housing societies, and private landholders.',
                'typical_process': '1. Structural & FSI feasibility report -> 2. General Body consent & legal tender -> 3. Builder selection & tripartite agreement -> 4. Municipal approval -> 5. Construction & possession.',
                'pricing_guideline': 'Advisory fee or turnkey joint development model based on project scale.',
                'safety_boundary': '75%+ general body consensus and RERA-compliant agreements required prior to commencement.'
            },
            {
                'category': 'nri_services',
                'topic': 'NRI Remote Property Stewardship & Construction Oversight',
                'keywords': 'nri, overseas owner, remote supervision, drone survey, boundary audit, tenant handover',
                'approved_content': 'Our NRI Property Stewardship provides overseas owners with trusted, independent representation in India. Services include quarterly 4K drone videography, milestone construction quality inspections, legal boundary encroachment checks, and turnkey flat renovation management with real-time video reporting.',
                'who_is_it_for': 'Non-Resident Indians (NRIs) and PIOs owning properties or building homes in India.',
                'typical_process': '1. Digital engagement & property onboarding -> 2. Baseline chartered engineer audit -> 3. Scheduled drone/physical visits -> 4. Portal dashboard reporting with milestone verification.',
                'pricing_guideline': 'Annual stewardship retainers or project-based milestone supervision fees.',
                'safety_boundary': 'Operates under strict legal power-of-attorney boundaries or advisory agreement.'
            },
            {
                'category': 'finance',
                'topic': 'Construction & Renovation Loan Advisory',
                'keywords': 'construction loan, home loan, renovation finance, bank estimate, boq for loan',
                'approved_content': 'We assist property owners with approved architectural drawings, chartered engineer detailed cost estimates (BOQ), and bank valuation documentation needed to apply for home construction and renovation loans from leading nationalized and private banks.',
                'who_is_it_for': 'Borrowers seeking construction or home improvement financing.',
                'typical_process': '1. Project BOQ preparation -> 2. Valuation & drawing compilation -> 3. Submission assistance to partner lending institutions.',
                'pricing_guideline': 'Complimentary with turnkey construction and renovation contracts.',
                'safety_boundary': 'BUILD+ is an engineering consultancy, not a direct bank or financial lender. Loan approvals are determined solely by lending institutions.'
            }
        ]

        for item_data in items:
            obj, created = AIKnowledgeItem.objects.update_or_create(
                category=item_data['category'],
                topic=item_data['topic'],
                defaults=item_data
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} knowledge snippet: {obj.topic}")

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(items)} AI knowledge items!"))
