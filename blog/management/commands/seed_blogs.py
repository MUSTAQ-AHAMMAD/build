import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from blog.models import BlogCategory, BlogPost
from core.models import WebsiteSettings, FAQ, Testimonial

class Command(BaseCommand):
    help = 'Seeds database with essential Blog categories, sample expert articles, and global website settings'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Initializing seed data for BUILD+ Construction Portal..."))

        # 1. Ensure Superuser / Staff User
        admin_user, created = User.objects.get_or_create(username='admin')
        if created:
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.email = 'admin@buildplus.com'
            admin_user.first_name = 'Portal'
            admin_user.last_name = 'Administrator'
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin123"))

        # 2. Website Settings
        settings = WebsiteSettings.load()
        settings.site_name = "BUILD+ Construction & Property Solutions"
        settings.tagline = "Build Better. Renovate Smarter. Rebuild with Confidence."
        settings.primary_phone = "+91 98765 43210"
        settings.whatsapp_number = "+91 98765 43210"
        settings.primary_email = "consult@buildplus.com"
        settings.office_address = "Suite 502, Builders Tower, Financial District, Hyderabad, India"
        settings.years_experience = 18
        settings.projects_completed = 520
        settings.happy_clients = 680
        settings.save()

        # 3. Blog Categories
        categories_data = [
            {
                'name': 'Flat & Apartment Renovation',
                'slug': 'flat-apartment-renovation',
                'description': 'Guides on complete flat renovation, interior upgrades, old apartment repairs, plumbing, electrical, and structural restoration.',
                'display_order': 1
            },
            {
                'name': 'Construction Services',
                'slug': 'construction-services',
                'description': 'Comprehensive insights into new home construction, multi-floor residential buildings, villas, commercial complexes, and industrial structures.',
                'display_order': 2
            },
            {
                'name': 'Demolition & Site Clearance',
                'slug': 'demolition-site-clearance',
                'description': 'Safety protocols, residential and commercial building demolition, internal flat dismantling, debris clearing, and site preparation.',
                'display_order': 3
            },
            {
                'name': 'Reconstruction & Rebuilding',
                'slug': 'reconstruction-rebuilding',
                'description': 'Rebuilding structures after planned demolition, fire damage, or structural obsolescence.',
                'display_order': 4
            },
            {
                'name': 'Property Redevelopment',
                'slug': 'property-redevelopment',
                'description': 'Redeveloping old buildings, society apartment redevelopments, joint ventures, and underutilized plot transformations.',
                'display_order': 5
            },
            {
                'name': 'Property & Land Advisory',
                'slug': 'property-land-advisory',
                'description': 'Advisory for property and land buying, selling assistance, legal boundary inspections, and property maintenance.',
                'display_order': 6
            },
            {
                'name': 'NRI Property Services',
                'slug': 'nri-property-services',
                'description': 'Dedicated coordination for non-resident Indians managing local construction, flat renovation, site inspections, and legal documentation.',
                'display_order': 7
            },
            {
                'name': 'Construction Loans & Finance',
                'slug': 'construction-loans-finance',
                'description': 'Financial planning, home construction loans, renovation funding, mortgage documentation, and bank valuation guidance.',
                'display_order': 8
            },
        ]

        cat_map = {}
        for cdata in categories_data:
            cat, _ = BlogCategory.objects.get_or_create(
                slug=cdata['slug'],
                defaults={
                    'name': cdata['name'],
                    'description': cdata['description'],
                    'display_order': cdata['display_order'],
                    'status': 'active'
                }
            )
            cat_map[cdata['slug']] = cat

        self.stdout.write(self.style.SUCCESS(f"Configured {len(cat_map)} Blog Categories."))

        # 4. Sample Articles
        articles_data = [
            {
                'title': 'Complete Flat Renovation Guide: Transforming Resale & Old Apartments',
                'slug': 'complete-flat-renovation-guide',
                'category': cat_map['flat-apartment-renovation'],
                'author': 'Er. Rajesh Varma, Principal Structural Engineer',
                'short_description': 'A complete step-by-step engineering and design roadmap for renovating 15 to 30-year-old flats, covering MEP overhauls, bathroom waterproofing, and modern modular layouts.',
                'related_service_type': 'flat_renovation',
                'featured': True,
                'status': 'published',
                'published_date': timezone.now() - timezone.timedelta(days=2),
                'seo_title': 'Complete Flat Renovation Guide for Resale & Old Apartments | BUILD+',
                'seo_description': 'Learn how to plan and execute a complete flat renovation. Structural checks, plumbing line replacement, electrical rewiring, and bathroom waterproofing.',
                'seo_keywords': 'flat renovation, old apartment remodel, resale flat renovation, apartment interior upgrade',
                'content': """<p class="lead">Acquiring an older resale flat or deciding to modernize your existing family apartment is one of the most rewarding property investments. However, flats that are 15 to 30 years old often harbor legacy issues that standard cosmetic painting cannot resolve.</p>

<h3>1. Structural & Concealed MEP Evaluation</h3>
<p>Before selecting tile patterns or modular cabinetry, a thorough engineering inspection of the concealed mechanical, electrical, and plumbing (MEP) infrastructure is non-negotiable:</p>
<ul>
    <li><strong>Plumbing Line Upgrades:</strong> Older apartments frequently rely on GI (galvanized iron) pipes that suffer from internal corrosion and limescale constriction. We replace them entirely with CPVC or multi-layer composite pipes.</li>
    <li><strong>Electrical Rewiring:</strong> Legacy aluminum or undersized copper wires cannot support modern HVAC loads, induction cooktops, and geysers. Dedicated 3-phase distribution boards with MCBs and RCCBs are installed.</li>
    <li><strong>Balcony & Wet Area Waterproofing:</strong> To permanently solve seepage into lower-floor flats, existing floor tiles are stripped to the RCC slab for high-performance polyurethane elastomeric waterproofing.</li>
</ul>

<h3>2. Open-Concept Space Optimization</h3>
<p>Older apartments were often designed with partitioned, dim layouts. By selectively removing non-load-bearing brick masonry partitions, we introduce contemporary open-concept living-dining configurations and expanded modular kitchens without compromising the building's structural load paths.</p>

<blockquote>
    "Quality flat renovation is 70% technical infrastructure and 30% aesthetics. Getting the concealed plumbing and waterproofing right protects your interior finishes for decades."
</blockquote>

<h3>3. Renovation Stage Checklist</h3>
<ol>
    <li>Society NOC and working hours approval.</li>
    <li>Controlled internal dismantling and debris carting.</li>
    <li>Core MEP rough-ins and wall chasing.</li>
    <li>Waterproofing barrier application and 48-hour ponding test.</li>
    <li>False ceiling framing, flooring installation, and primer coats.</li>
    <li>Modular joinery, sanitary fixtures, and final premium finish.</li>
</ol>"""
            },
            {
                'title': 'Flat Renovation vs Reconstruction: How to Decide for Aging Properties',
                'slug': 'flat-renovation-vs-reconstruction',
                'category': cat_map['flat-apartment-renovation'],
                'author': 'Ananya Roy, Senior Architect',
                'short_description': 'Struggling to choose between structural renovation and full property reconstruction? Discover key assessment criteria including RCC health, cost thresholds, and FSI utilization.',
                'related_service_type': 'flat_renovation',
                'featured': True,
                'status': 'published',
                'published_date': timezone.now() - timezone.timedelta(days=5),
                'seo_title': 'Flat Renovation vs Reconstruction: Complete Decision Matrix | BUILD+',
                'seo_description': 'Compare renovation vs reconstruction costs, structural lifespan, and approval requirements for aging buildings and residential flats.',
                'seo_keywords': 'renovation vs reconstruction, old building repair, rebuild flat, structural assessment',
                'content': """<p class="lead">When a residential structure reaches 30 to 45 years of age, property owners and resident associations face a critical crossroad: Should the building undergo deep structural renovation, or is complete demolition and reconstruction the more economically viable route?</p>

<h3>The Decision Matrix: Key Engineering Factors</h3>
<table class="table table-bordered my-4">
    <thead class="table-dark">
        <tr>
            <th>Parameter</th>
            <th>Renovation & Restoration</th>
            <th>Demolition & Reconstruction</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Structural Integrity</strong></td>
            <td>RCC columns and beams have surface spalling with &lt; 15% rebar corrosion.</td>
            <td>Extensive carbonation, foundation settlement, or column core degradation.</td>
        </tr>
        <tr>
            <td><strong>Cost-to-New Ratio</strong></td>
            <td>Repair cost is under 30–35% of a new construction build.</td>
            <td>Repair cost exceeds 45–50% of new construction value.</td>
        </tr>
        <tr>
            <td><strong>FSI / Layout Upgrade</strong></td>
            <td>Existing footprint is preserved; internal partitions altered.</td>
            <td>Unlocks modern building bylaws, additional floors, and stilt parking.</td>
        </tr>
        <tr>
            <td><strong>Execution Time</strong></td>
            <td>2 to 4 months per unit.</td>
            <td>12 to 24 months for multi-unit apartment complexes.</td>
        </tr>
    </tbody>
</table>

<h3>When Structural Strengthening is Best</h3>
<p>If ultrasonic pulse velocity (UPV) and rebound hammer tests demonstrate solid core concrete strength, micro-concrete jacketing of columns, epoxy grouting, and sacrificial anode cathodic protection can extend building life by another 20–25 years at a fraction of rebuilding costs.</p>"""
            },
            {
                'title': 'When Should You Demolish an Old Building? Structural Indicators & Safety Norms',
                'slug': 'when-to-demolish-an-old-building',
                'category': cat_map['demolition-site-clearance'],
                'author': 'Er. Rajesh Varma, Structural Specialist',
                'short_description': 'Detailed breakdown of critical signs indicating an old building must be razed. Safety protocols, controlled demolition methods, and local municipal compliance.',
                'related_service_type': 'demolition',
                'featured': False,
                'status': 'published',
                'published_date': timezone.now() - timezone.timedelta(days=8),
                'seo_title': 'When Should You Demolish an Old Building? Critical Signs & Process',
                'seo_description': 'Essential guide on building demolition indicators: foundation settlement, structural distress, municipal notices, and controlled razing safety.',
                'seo_keywords': 'building demolition, when to demolish, site clearing, demolition safety norms',
                'content': """<p class="lead">Demolishing a building is a weighty decision that blends structural safety, legal compliance, and economic foresight. Continuing to inhabit or patch a structurally condemned property exposes occupants to severe hazards.</p>

<h3>Top 4 Triggers for Building Demolition</h3>
<ul>
    <li><strong>Severe Structural Distress:</strong> Deep diagonal shear cracks traversing major load-bearing columns and transfer girders that cannot be economically jacketed.</li>
    <li><strong>Foundation Settlement:</strong> Differential ground settlement causing unrectifiable structural tilts or sub-slab voids.</li>
    <li><strong>Municipal Condemnation Notices:</strong> Structural audits categorized under unsafe or dilapidated classifications (e.g. C-1 grade notices).</li>
    <li><strong>Plot Optimization for Redevelopment:</strong> Older single-story dwellings occupying prime urban land where revised zonal bylaws allow G+4 or higher multi-unit residential structures.</li>
</ul>

<h3>The Controlled Demolition Methodology</h3>
<p>Modern building demolition in dense urban neighborhoods requires surgical control. High-reach excavators, diamond wire saw cutting, water mist cannons for dust suppression, and acoustic sound curtains ensure zero damage to adjacent neighboring structures.</p>"""
            },
            {
                'title': 'Apartment Redevelopment: What Property Owners & Societies Should Know',
                'slug': 'apartment-redevelopment-guide',
                'category': cat_map['property-redevelopment'],
                'author': 'BUILD+ Legal & Advisory Cell',
                'short_description': 'Essential guide for apartment owners navigating redevelopment: consensus building, joint development agreements (JDA), carpet area increments, and developer vetting.',
                'related_service_type': 'redevelopment',
                'featured': True,
                'status': 'published',
                'published_date': timezone.now() - timezone.timedelta(days=11),
                'seo_title': 'Apartment Redevelopment Guide: What Society Members Must Know',
                'seo_description': 'Navigate apartment redevelopment with confidence. JDA structuring, transit rent, carpet area expansion, and construction supervision.',
                'seo_keywords': 'apartment redevelopment, society redevelopment, property reconstruction, JDA',
                'content': """<p class="lead">For aging housing societies built in the 1980s and 1990s, redevelopment represents a transformative opportunity: replacing cramped, deteriorating units with modern luxury apartments, elevator access, dedicated covered parking, and significant capital appreciation.</p>

<h3>Key Milestones in Society Redevelopment</h3>
<ol>
    <li><strong>General Body Resolution:</strong> Achieving consensus among members (as mandated by local state cooperative acts).</li>
    <li><strong>Feasibility Report:</strong> Structural audit, title search, and architect-led calculation of permissible TDR (Transferable Development Rights) and FSI.</li>
    <li><strong>Tender & Developer Selection:</strong> Drafting transparent tender documents specifying minimum carpet area increment, corpus fund, and monthly transit rent for temporary relocation.</li>
    <li><strong>Tripartite Agreement Execution:</strong> Legally binding agreements with escrow bank guarantees safeguarding construction milestones.</li>
</ol>"""
            },
            {
                'title': 'Complete Home Construction Process: From Foundation to Handover',
                'slug': 'complete-home-construction-process',
                'category': cat_map['construction-services'],
                'author': 'Er. K. S. Murthy, VP Projects',
                'short_description': 'A comprehensive walkthrough of building a custom residential home or independent villa. Soil testing, RCC framing, brickwork, MEP rough-ins, and final finishing.',
                'related_service_type': 'construction',
                'featured': False,
                'status': 'published',
                'published_date': timezone.now() - timezone.timedelta(days=14),
                'seo_title': 'Complete Home Construction Process: Step-by-Step Guide | BUILD+',
                'seo_description': 'Understand each phase of new home construction. Soil investigation, foundation design, curing cycles, brickwork, and turnkey project delivery.',
                'seo_keywords': 'home construction process, residential building stages, villa construction, turnkey construction',
                'content': """<p class="lead">Building a custom home or villa is an intricate engineering journey spanning several months. Knowing the precise milestones ensures you maintain quality oversight and budget discipline.</p>

<h3>The 6 Primary Construction Phases</h3>
<div class="row g-3 my-3">
    <div class="col-md-6"><div class="p-3 border rounded bg-light"><strong>1. Soil & Substructure:</strong> Soil core sampling, excavation, anti-termite treatment, PCC, and isolated/raft foundation casting.</div></div>
    <div class="col-md-6"><div class="p-3 border rounded bg-light"><strong>2. Superstructure RCC:</strong> Casting plinth beams, RCC columns, shuttering, slab reinforcement, and strict 21-day curing cycles.</div></div>
    <div class="col-md-6"><div class="p-3 border rounded bg-light"><strong>3. Masonry & Plastering:</strong> AAC block or red brick masonry with expansion joint reinforcement and double-coat external sand-faced plaster.</div></div>
    <div class="col-md-6"><div class="p-3 border rounded bg-light"><strong>4. Electrical & Plumbing:</strong> Concealed PVC conduit routing, fire-retardant wiring, CPVC pressure testing, and drainage soil stacks.</div></div>
    <div class="col-md-6"><div class="p-3 border rounded bg-light"><strong>5. Flooring & Wet Finishes:</strong> Vitrified/Italian marble installation, full-height bathroom dado tiles, and waterproofing.</div></div>
    <div class="col-md-6"><div class="p-3 border rounded bg-light"><strong>6. Final Detailing & Handover:</strong> Modular kitchen, interior carpentry, primer and 3-coat acrylic emulsion paint, and deep cleaning.</div></div>
</div>"""
            },
            {
                'title': 'Structural Renovation of Old Buildings: Strengthening Columns, Beams & Slabs',
                'slug': 'structural-renovation-of-old-buildings',
                'category': cat_map['flat-apartment-renovation'],
                'author': 'Er. Rajesh Varma, Principal Structural Engineer',
                'short_description': 'How advanced civil retrofitting techniques like column jacketing, carbon fiber wrapping (CFRP), and epoxy injection restore aging concrete structures.',
                'related_service_type': 'flat_renovation',
                'featured': False,
                'status': 'published',
                'published_date': timezone.now() - timezone.timedelta(days=18),
                'seo_title': 'Structural Renovation & Column Jacketing Guide | BUILD+',
                'seo_description': 'Discover retrofitting techniques for old buildings. Concrete jacketing, micro-concrete repairs, and carbon fiber reinforcement (CFRP).',
                'seo_keywords': 'structural renovation, column jacketing, CFRP wrapping, building restoration',
                'content': """<p class="lead">When environmental weathering and age-related carbonation degrade reinforced concrete, structural retrofitting provides an engineered alternative to costly demolition.</p>

<h3>Standard Retrofitting Techniques</h3>
<ul>
    <li><strong>RC Column Jacketing:</strong> Chipping deteriorated cover, cleaning rusted rebar, anchoring supplemental steel ties, and encasing the column with self-compacting micro-concrete.</li>
    <li><strong>Carbon Fiber Reinforced Polymer (CFRP):</strong> High-tensile composite wrapping providing immense shear and flexural strengthening without adding dead weight to the structure.</li>
    <li><strong>Slab Polymer Modified Mortar (PMM) Repairs:</strong> Treating delaminated ceilings and exposed slab rebars with zinc-rich anti-corrosion primers and structural repair mortars.</li>
</ul>"""
            },
            {
                'title': 'Demolition and Reconstruction Process: Controlled Razing to New Foundations',
                'slug': 'demolition-and-reconstruction-process',
                'category': cat_map['reconstruction-rebuilding'],
                'author': 'BUILD+ Project Operations',
                'short_description': 'How our team orchestrates seamless transitions from old structure razing and debris clearance directly into new foundation engineering and construction.',
                'related_service_type': 'reconstruction',
                'featured': False,
                'status': 'published',
                'published_date': timezone.now() - timezone.timedelta(days=22),
                'seo_title': 'Demolition and Reconstruction Process: Seamless Rebuilding Guide',
                'seo_description': 'Learn how site demolition transitions into new foundation engineering, municipal permissions, and modern reconstruction.',
                'seo_keywords': 'demolition and reconstruction, site clearing, rebuilding damaged property',
                'content': """<p class="lead">Demolition and reconstruction should never be managed as disconnected contracts. Integrating both under a unified project manager ensures smooth site clearance, soil testing, and rapid foundation commencement.</p>

<h3>Key Integration Benefits</h3>
<ul>
    <li>Single-point accountability from permit acquisition to final structure delivery.</li>
    <li>Direct reuse of processed masonry hardcore for sub-base grading where appropriate.</li>
    <li>Elimination of costly idle gaps between demolition contractors and construction crews.</li>
</ul>"""
            },
            {
                'title': 'NRI Property Management Guide: Protecting & Monitoring Indian Real Estate Assets from Abroad',
                'slug': 'nri-property-management-guide',
                'category': cat_map['nri-property-services'],
                'author': 'Vikram Mehra, NRI Client Relations Director',
                'short_description': 'Essential protocol for non-resident property owners. Regular physical boundary inspections, tenant management, renovation supervision, and legal safeguarding.',
                'related_service_type': 'nri_services',
                'featured': True,
                'status': 'published',
                'published_date': timezone.now() - timezone.timedelta(days=25),
                'seo_title': 'NRI Property Management & Construction Supervision Guide | BUILD+',
                'seo_description': 'Protect and monitor Indian real estate from abroad. On-site property inspection, boundary security, renovation supervision, and legal assistance.',
                'seo_keywords': 'NRI property management, overseas property supervision, India land maintenance, NRI renovation',
                'content': """<p class="lead">Living thousands of miles away while owning flats, independent plots, or ancestral properties in India presents distinct challenges: encroachment risks, utility neglect, tenant disputes, and the inability to supervise on-site construction.</p>

<h3>Our Dedicated NRI Service Suite</h3>
<div class="row g-3 my-3">
    <div class="col-md-6"><div class="p-3 border rounded bg-light"><strong>Geo-Tagged Video Inspections:</strong> Quarterly photographic audits documenting plot boundaries, structural condition, and perimeter security.</div></div>
    <div class="col-md-6"><div class="p-3 border rounded bg-light"><strong>Turnkey Renovation Supervision:</strong> Complete project management for ancestral or resale flats with digital milestone sign-offs.</div></div>
    <div class="col-md-6"><div class="p-3 border rounded bg-light"><strong>Municipal & Tax Compliance:</strong> Managing property tax assessments, utility meter transfers, and mutation records.</div></div>
    <div class="col-md-6"><div class="p-3 border rounded bg-light"><strong>Buy & Sell Escrow Assistance:</strong> Verified legal title diligence, valuation appraisals, and power of attorney coordination.</div></div>
</div>"""
            },
            {
                'title': 'Construction Cost Planning: Budgeting Material, Labor & Civil Schedules',
                'slug': 'construction-cost-planning',
                'category': cat_map['construction-services'],
                'author': 'S. Venkat, Quantity Surveyor & Estimator',
                'short_description': 'Comprehensive framework for estimating construction budgets. Material price fluctuation buffers, labor allocations, and BOQ transparency.',
                'related_service_type': 'construction',
                'featured': False,
                'status': 'published',
                'published_date': timezone.now() - timezone.timedelta(days=28),
                'seo_title': 'Construction Cost Planning & BOQ Budgeting Guide | BUILD+',
                'seo_description': 'Master construction cost planning. Material ratios, labor expenditure, BOQ formulation, and strategies to prevent project cost overruns.',
                'seo_keywords': 'construction cost planning, civil budgeting, BOQ estimation, building cost per sqft',
                'content': """<p class="lead">Accurate cost forecasting is the cornerstone of stress-free construction. Understanding cost distribution across cement, steel, sand, labor, and finishing materials prevents unexpected mid-project delays.</p>

<h3>Standard Cost Breakdown for Residential Projects</h3>
<ul>
    <li><strong>Structural Frame (Cement, TMT Steel, Aggregates, Sand):</strong> ~35–40% of total budget.</li>
    <li><strong>Masonry, Plastering & Waterproofing:</strong> ~15–18% of total budget.</li>
    <li><strong>MEP (Electrical, Plumbing, Sanitary):</strong> ~12–15% of total budget.</li>
    <li><strong>Finishes (Flooring, Painting, Joinery, Windows):</strong> ~25–30% of total budget.</li>
</ul>"""
            },
            {
                'title': 'Renovation Planning Checklist: Essential Steps Before Stripping Walls & Concealed MEP',
                'slug': 'renovation-planning-checklist',
                'category': cat_map['flat-apartment-renovation'],
                'author': 'BUILD+ Quality Audit Team',
                'short_description': '10-point pre-renovation checklist covering noise permits, neighbor notifications, temporary utility shutoffs, and contingency budgets.',
                'related_service_type': 'flat_renovation',
                'featured': False,
                'status': 'published',
                'published_date': timezone.now() - timezone.timedelta(days=32),
                'seo_title': 'Renovation Planning Checklist: 10 Critical Pre-Work Steps',
                'seo_description': 'Essential checklist before starting home or flat renovation. Society NOCs, main valve shutoffs, dust control, and milestone schedules.',
                'seo_keywords': 'renovation checklist, flat remodel planning, home improvement checklist',
                'content': """<p class="lead">Smooth flat renovations rely on rigorous pre-work preparation. Before civil workers make the first hammer strike, verify these vital prerequisites:</p>

<h3>The 10-Point Pre-Renovation Checklist</h3>
<ol>
    <li>Secure written society/RWA permissions and adhere to permissible daily working hours.</li>
    <li>Notify immediate floor neighbors to foster goodwill and preempt noise complaints.</li>
    <li>Locate and test main water stopcocks and electrical mains isolating the unit.</li>
    <li>Cover common corridor elevators and floors with protective corrugated sheets.</li>
    <li>Erect zippered plastic dust barriers isolating non-work zones.</li>
    <li>Verify that the structural engineer has approved all planned wall knock-downs.</li>
    <li>Confirm tile, sanitary ware, and paint code lead times with suppliers.</li>
    <li>Designate a dedicated municipal debris carting schedule.</li>
    <li>Ensure all on-site contractors have valid third-party liability insurance.</li>
    <li>Keep an 8–10% financial contingency reserve readily accessible.</li>
</ol>"""
            },
        ]

        for adata in articles_data:
            BlogPost.objects.get_or_create(
                slug=adata['slug'],
                defaults=adata
            )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(articles_data)} professional Blog articles."))

        # 5. Seed Core FAQs
        faqs_data = [
            {
                'category': 'renovation',
                'question': 'Do you undertake complete renovation for old and resale flats?',
                'answer': 'Yes. We specialize in comprehensive flat and apartment renovations, including plumbing replacement, electrical rewiring, waterproofing, wall modifications, modular kitchens, bathrooms, flooring, and false ceilings.'
            },
            {
                'category': 'demolition',
                'question': 'Can you handle both building demolition and subsequent reconstruction?',
                'answer': 'Absolutely. We provide an integrated single-window service managing structural assessment, municipal demolition permits, safe controlled razing, debris clearing, and subsequent new building reconstruction.'
            },
            {
                'category': 'nri',
                'question': 'How do you support property owners and NRIs living outside India?',
                'answer': 'We offer dedicated NRI services featuring quarterly geo-tagged photo/video property audits, turnkey flat renovation supervision, plot encroachment protection, tax compliance, and transparent digital milestone reporting.'
            },
            {
                'category': 'construction',
                'question': 'Can I request an engineer site visit before committing to a contract?',
                'answer': 'Yes. You can use our online Site Visit Request form or contact us directly. Our senior civil engineer will visit the property, evaluate the condition, and prepare a detailed preliminary estimate and scope of work.'
            },
            {
                'category': 'finance',
                'question': 'Do you assist with construction and renovation loans?',
                'answer': 'Yes. We assist clients with bank-approved technical estimates, BOQs, building plan sanction documentation, and stage-wise valuation certificates for leading financial institutions.'
            }
        ]

        for fdata in faqs_data:
            FAQ.objects.get_or_create(
                question=fdata['question'],
                defaults=fdata
            )

        # 6. Seed Testimonials
        testimonials_data = [
            {
                'client_name': 'K. S. Narayana Rao',
                'client_title': 'Apartment Owner, 25-Year-Old 3BHK Flat',
                'service_rendered': 'Complete Flat Renovation & MEP Overhaul',
                'feedback': 'BUILD+ transformed our 25-year-old flat into a brand-new contemporary luxury home. Their civil team replaced all legacy GI plumbing pipes, rectified persistent balcony dampness, and completed the work on schedule.',
                'rating': 5,
                'is_featured': True
            },
            {
                'client_name': 'Suresh & Malathi Reddy',
                'client_title': 'NRI Property Investors, California USA',
                'service_rendered': 'NRI Property Supervision & Villa Construction',
                'feedback': 'Managing property from overseas used to be stressful until we partnered with BUILD+. Their weekly video logs, transparent material billing, and strict milestone adherence gave us total peace of mind.',
                'rating': 5,
                'is_featured': True
            },
            {
                'client_name': 'G. Madhavan',
                'client_title': 'Commercial Property Owner',
                'service_rendered': 'Demolition & Commercial Reconstruction',
                'feedback': 'Controlled demolition of our old commercial building in a tight street was handled flawlessly without causing any disturbance to adjoining properties. Rebuilding was completed 3 weeks ahead of schedule.',
                'rating': 5,
                'is_featured': True
            }
        ]

        for tdata in testimonials_data:
            Testimonial.objects.get_or_create(
                client_name=tdata['client_name'],
                defaults=tdata
            )

        self.stdout.write(self.style.SUCCESS("All seed data created successfully!"))
