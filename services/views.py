from django.shortcuts import render, get_object_or_404
from .models import ServiceCategory, Service
from blog.models import BlogPost, BlogCategory

SUBSERVICE_DATA = {
    # Construction
    'residential': {
        'title': 'Residential House Construction',
        'category': 'Construction Services',
        'hero_subtitle': 'Turnkey independent homes, G+1 and multi-floor residences engineered with premium structural specifications and on-time delivery.',
        'icon': '🏠',
        'features': [
            'Architectural 2D/3D floor planning & structural modeling',
            'Soil core investigation & customized foundation engineering',
            '21-day strict RCC water curing protocols',
            'Double-coat sand faced external plastering & heat-reflective coats',
            'Full turnkey MEP and interior woodwork handover'
        ],
        'blog_cat_slug': 'construction-services'
    },
    'apartments': {
        'title': 'Apartment Building Construction',
        'category': 'Construction Services',
        'hero_subtitle': 'Multi-unit residential construction for landowners and builders. Maximizing permissible FSI with modern stilt parking and elevators.',
        'icon': '🏢',
        'features': [
            'Multi-floor RCC framed construction with seismic resistance',
            'Stilt parking layout, dual lift shafts, and fire safety systems',
            'Municipal sanction approvals, building plan permissions, and occupancy NOC',
            'Dedicated rainwater harvesting and underground water sumps',
            'Turnkey individual flat finishing with premium vitrified tiles'
        ],
        'blog_cat_slug': 'construction-services'
    },
    'villas': {
        'title': 'Custom Villa Construction',
        'category': 'Construction Services',
        'hero_subtitle': 'Bespoke contemporary and classical villas designed for luxury living, private swimming pools, landscape architecture, and home automation.',
        'icon': '🏰',
        'features': [
            'Custom double-height living foyers and cantilevered balconies',
            'Imported Italian marble, hardwood joinery, and thermal glass glazing',
            'Private swimming pool and landscape garden irrigation engineering',
            'Smart home automation and solar rooftop infrastructure',
            'Turnkey architectural sign-off and multi-year structural warranty'
        ],
        'blog_cat_slug': 'construction-services'
    },
    'commercial': {
        'title': 'Commercial Building Construction',
        'category': 'Construction Services',
        'hero_subtitle': 'Modern corporate offices, retail spaces, and mixed-use commercial properties built with high-load floor plates and energy-efficient façades.',
        'icon': '🏬',
        'features': [
            'High-load RCC transfer slabs for open retail floor plans',
            'Structural glass curtain wall glazing and acoustic insulation',
            'Centralized HVAC ducting and high-capacity electrical sub-stations',
            'Multi-level basement parking and fire hydrant networks',
            'RERA and municipal commercial licensing compliance'
        ],
        'blog_cat_slug': 'construction-services'
    },

    # Renovation
    'flats': {
        'title': 'Complete Flat Renovation',
        'category': 'Flat & Apartment Renovation',
        'hero_subtitle': 'Complete modernization of 15 to 30-year-old resale, rental, or occupied flats. Replacing legacy GI plumbing, wiring, and creating open-plan layouts.',
        'icon': '✨',
        'features': [
            'Complete replacement of legacy galvanized plumbing with CPVC/PEX',
            '3-phase electrical rewiring with dedicated AC and appliance circuits',
            '100% leak-proof bathroom and balcony polyurethane waterproofing',
            'Selective non-load-bearing wall removal for open-concept layouts',
            'Designer false ceilings, premium LED profile lighting, and modular kitchen'
        ],
        'blog_cat_slug': 'flat-apartment-renovation'
    },
    'apartments': {
        'title': 'Apartment Society & Multi-Unit Renovation',
        'category': 'Flat & Apartment Renovation',
        'hero_subtitle': 'Renovation solutions for entire apartment blocks, society lobbies, exterior façades, common plumbing shafts, and terrace waterproofing.',
        'icon': '🏢',
        'features': [
            'Building exterior elastomeric weather-shield painting',
            'Terrace slab water-ponding tests and membrane waterproofing',
            'Overhaul of shared plumbing ducts, downpipes, and drainage sumps',
            'Entrance lobby, lift cladding, and common corridor modernization',
            'Society general body presentation and milestone-based sign-offs'
        ],
        'blog_cat_slug': 'flat-apartment-renovation'
    },
    'interior': {
        'title': 'Interior Remodeling & Upgrades',
        'category': 'Flat & Apartment Renovation',
        'hero_subtitle': 'Custom modular kitchens, luxury bathroom transformations, false ceiling lighting, and premium Italian marble polishing for existing homes.',
        'icon': '🛋️',
        'features': [
            'Marine-grade HDHMR modular kitchen cabinets with quartz countertops',
            'Full-height bathroom vitrified tiles and concealed diverter fittings',
            'False ceilings with ambient cove lighting and acoustic insulation',
            'Mirror-finish marble diamond polishing and PU wood polishing',
            'Custom wardrobe joinery and smart home touch switches'
        ],
        'blog_cat_slug': 'flat-apartment-renovation'
    },
    'structural': {
        'title': 'Structural Renovation & Concrete Repair',
        'category': 'Flat & Apartment Renovation',
        'hero_subtitle': 'Engineered retrofitting for aging RCC structures: column micro-concrete jacketing, carbon fiber wrapping (CFRP), and epoxy crack grouting.',
        'icon': '🧱',
        'features': [
            'Non-destructive testing (NDT): Rebound hammer and UPV testing',
            'Corrosion treatment and rust-converting epoxy rebar coatings',
            'Self-compacting micro-concrete column encasement',
            'CFRP composite wrapping for beam shear and flexural strengthening',
            'Polymer modified mortar (PMM) ceiling delamination repairs'
        ],
        'blog_cat_slug': 'flat-apartment-renovation'
    },

    # Demolition & Reconstruction
    'building-demolition': {
        'title': 'Controlled Building Demolition',
        'category': 'Demolition & Reconstruction',
        'hero_subtitle': 'Safe mechanical demolition for old, condemned, or obsolete residential and commercial buildings with zero disruption to adjoining structures.',
        'icon': '🏗️',
        'features': [
            'Structural stability audit and demolition permit acquisition',
            'High-reach excavator dismantling and diamond wire saw cutting',
            'Continuous mist spray water cannons for 90% dust suppression',
            'Acoustic sound curtains safeguarding neighboring properties',
            'Site barricading, utility isolation, and debris removal'
        ],
        'blog_cat_slug': 'demolition-site-clearance'
    },
    'flat-demolition': {
        'title': 'Flat Internal Demolition & Strip-Outs',
        'category': 'Demolition & Reconstruction',
        'hero_subtitle': 'Controlled internal strip-outs of floor tiles, bathroom walls, fixtures, and non-load-bearing brick masonry partitions prior to full flat renovation.',
        'icon': '🔨',
        'features': [
            'Society working hour compliance and elevator protection padding',
            'Careful removal of non-bearing brick masonry walls',
            'Tile chipping to bare RCC slab for fresh waterproofing',
            'Safe removal of legacy concealed wiring and plumbing lines',
            'Daily scheduled bagged debris hauling to municipal dumping yards'
        ],
        'blog_cat_slug': 'demolition-site-clearance'
    },
    'site-clearing': {
        'title': 'Site Clearing & Earth Preparation',
        'category': 'Demolition & Reconstruction',
        'hero_subtitle': 'Clearing masonry rubble, vegetation, underground roots, and leveling plots for immediate new foundation commencement.',
        'icon': '🚜',
        'features': [
            'Heavy excavator rubble carting and recycling',
            'Tree root grubbing and organic soil stripping',
            'Plot contour leveling and sub-grade compaction',
            'Anti-termite chemical soil barrier treatment',
            'Perimeter boundary marking and security sheet fencing'
        ],
        'blog_cat_slug': 'demolition-site-clearance'
    },
    'reconstruction': {
        'title': 'Reconstruction & Rebuilding Services',
        'category': 'Demolition & Reconstruction',
        'hero_subtitle': 'Seamless rebuilding following demolition or structural obsolescence. Integrating razing, soil testing, and new construction under one contract.',
        'icon': '↻',
        'features': [
            'Single contract transition from demolition to new foundation',
            'Soil core sampling and updated architectural structural design',
            'Elimination of contractor idle time between demolition and civil works',
            'Reuse of processed masonry hardcore for sub-base grading',
            'Turnkey milestone-based project execution and handover'
        ],
        'blog_cat_slug': 'reconstruction-rebuilding'
    },

    # Redevelopment
    'property': {
        'title': 'Old Property Redevelopment',
        'category': 'Redevelopment Services',
        'hero_subtitle': 'Unlocking immense capital value by redeveloping aging single-family homes into modern multi-floor residential buildings.',
        'icon': '◇',
        'features': [
            'Plot feasibility study and revised FSI/TDR calculation',
            'Joint Development Agreement (JDA) structuring',
            'Turnkey demolition, architectural approval, and construction',
            'Owner share allocation and rental compensation models',
            'Modern amenities: Stilt parking, elevator, solar grid, and terrace lounge'
        ],
        'blog_cat_slug': 'property-redevelopment'
    },
    'apartment': {
        'title': 'Apartment Society Redevelopment',
        'category': 'Redevelopment Services',
        'hero_subtitle': 'Revitalizing 30+ year old housing societies. Providing existing members with expanded carpet area, corpus funds, and modern towers.',
        'icon': '🏢',
        'features': [
            'Society general body meeting facilitation and resolution documentation',
            'Structural audit reports and municipal sanction drafting',
            'Transparent bidding and developer vetting with bank guarantee escrows',
            'Monthly transit rent for members during construction period',
            'Delivery of modern luxury apartments with dedicated parking bays'
        ],
        'blog_cat_slug': 'property-redevelopment'
    },
}


def service_home(request):
    """Overview of all primary services"""
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related('services')
    return render(request, 'services/service_list.html', {'categories': categories})


def construction_view(request, subservice=None):
    """Construction services page or subservice deep-dive"""
    sub_data = SUBSERVICE_DATA.get(subservice) if subservice else None
    related_guides = BlogPost.objects.filter(status='published', category__slug='construction-services')[:3]
    context = {
        'subservice': subservice,
        'sub_data': sub_data,
        'related_guides': related_guides,
    }
    return render(request, 'services/construction.html', context)


def renovation_view(request, subservice=None):
    """Dedicated Flat & Apartment Renovation page or subservice deep-dive"""
    sub_data = SUBSERVICE_DATA.get(subservice) if subservice else None
    related_guides = BlogPost.objects.filter(status='published', category__slug='flat-apartment-renovation')[:3]
    context = {
        'subservice': subservice,
        'sub_data': sub_data,
        'related_guides': related_guides,
    }
    return render(request, 'services/renovation.html', context)


def demolition_view(request, subservice=None):
    """Demolition & Reconstruction page or subservice deep-dive"""
    sub_data = SUBSERVICE_DATA.get(subservice) if subservice else None
    related_guides = BlogPost.objects.filter(status='published', category__slug__in=['demolition-site-clearance', 'reconstruction-rebuilding'])[:3]
    context = {
        'subservice': subservice,
        'sub_data': sub_data,
        'related_guides': related_guides,
    }
    return render(request, 'services/demolition.html', context)


def redevelopment_view(request, subservice=None):
    """Redevelopment page or subservice deep-dive"""
    sub_data = SUBSERVICE_DATA.get(subservice) if subservice else None
    related_guides = BlogPost.objects.filter(status='published', category__slug='property-redevelopment')[:3]
    context = {
        'subservice': subservice,
        'sub_data': sub_data,
        'related_guides': related_guides,
    }
    return render(request, 'services/redevelopment.html', context)


def property_land_view(request):
    """Property & Land Services page"""
    related_guides = BlogPost.objects.filter(status='published', category__slug='property-land-advisory')[:3]
    return render(request, 'services/property.html', {'related_guides': related_guides})


def nri_services_view(request):
    """NRI Property Services page"""
    related_guides = BlogPost.objects.filter(status='published', category__slug='nri-property-services')[:3]
    return render(request, 'services/nri.html', {'related_guides': related_guides})


def finance_view(request):
    """Construction Loans & Finance Assistance page"""
    related_guides = BlogPost.objects.filter(status='published', category__slug='construction-loans-finance')[:3]
    return render(request, 'services/finance.html', {'related_guides': related_guides})


def property_inspection_view(request):
    """Property Inspection & Structural Assessment Coordination"""
    related_guides = BlogPost.objects.filter(status='published', category__slug='property-land-advisory')[:3]
    return render(request, 'services/property.html', {
        'related_guides': related_guides,
        'is_inspection': True,
        'page_title': 'Property Inspection & Engineering Condition Assessment',
        'hero_subtitle': 'Pre-purchase structural audits, old building health evaluations, crack & dampness core diagnostics, and renovation feasibility reports.'
    })


def government_approvals_view(request):
    """Government Approvals & Municipal Compliance Coordination"""
    related_guides = BlogPost.objects.filter(status='published', category__slug='government-documentation')[:3]
    return render(request, 'services/property.html', {
        'related_guides': related_guides,
        'is_government': True,
        'page_title': 'Government Approvals & Municipal Sanction Coordination',
        'hero_subtitle': 'End-to-end liaison assistance for building plan permissions, demolition NOCs, fire compliance, Khata mutation, and occupancy certificates.'
    })


def property_documentation_view(request):
    """Property Documentation & Title Record Coordination"""
    related_guides = BlogPost.objects.filter(status='published', category__slug='government-documentation')[:3]
    return render(request, 'services/property.html', {
        'related_guides': related_guides,
        'is_documentation': True,
        'page_title': 'Property Documentation & Legal Title Preparation',
        'hero_subtitle': 'Collection, verification assistance, encumbrance certificates (EC), sale deed draft scrutiny, and municipal land record consolidation.'
    })


def legal_coordination_view(request):
    """Legal & Property Registration Professional Coordination"""
    related_guides = BlogPost.objects.filter(status='published', category__slug='government-documentation')[:3]
    return render(request, 'services/property.html', {
        'related_guides': related_guides,
        'is_legal': True,
        'page_title': 'Legal Professional & Sub-Registrar Registration Coordination',
        'hero_subtitle': 'Independent legal advocate liaison, title search reports, sale agreement preparation, and slot booking assistance at the sub-registrar office.'
    })


def repair_maintenance_view(request):
    """Structural Repair, Restoration & Annual Property Maintenance"""
    related_guides = BlogPost.objects.filter(status='published', category__slug='flat-apartment-renovation')[:3]
    return render(request, 'services/renovation.html', {
        'related_guides': related_guides,
        'subservice': 'structural',
        'page_title': 'Structural Repairs, Waterproofing & Property Restoration',
        'hero_subtitle': 'Pressure grouting, carbon fiber reinforcement, deep dampness rectification, elastomeric coating, and preventive maintenance.'
    })


def interior_remodeling_view(request):
    """Custom Interior Remodeling & Modular Upgrades"""
    related_guides = BlogPost.objects.filter(status='published', category__slug='flat-apartment-renovation')[:3]
    return render(request, 'services/renovation.html', {
        'related_guides': related_guides,
        'subservice': 'interior',
        'page_title': 'Complete Interior Remodeling & Modular Upgrades',
        'hero_subtitle': 'Bespoke HDHMR modular kitchens, designer false ceilings, LED profile lighting, Italian marble polishing, and luxury bathroom transformations.'
    })


def project_management_view(request):
    """Construction & Renovation Project Management Consultancy"""
    related_guides = BlogPost.objects.filter(status='published', category__slug='construction-services')[:3]
    return render(request, 'services/construction.html', {
        'related_guides': related_guides,
        'is_pmc': True,
        'page_title': 'Construction & Renovation Project Management (PMC)',
        'hero_subtitle': 'Single-point supervision, material quality testing, site engineer milestone tracking, contractor coordination, and weekly photographic reporting.'
    })


def service_category_detail(request, category_slug):
    """Dynamic Service Category Dispatcher"""
    if category_slug in ['construction', 'construction-services']:
        return construction_view(request)
    elif category_slug in ['renovation', 'flat-apartment-renovation']:
        return renovation_view(request)
    elif category_slug in ['demolition-reconstruction', 'demolition']:
        return demolition_view(request)
    elif category_slug in ['redevelopment', 'property-redevelopment']:
        return redevelopment_view(request)
    elif category_slug in ['property-land', 'land-property-services', 'property']:
        return property_land_view(request)
    elif category_slug in ['nri-services', 'nri-property-services', 'nri']:
        return nri_services_view(request)
    elif category_slug in ['construction-finance', 'bank-loan-finance-support', 'finance']:
        return finance_view(request)
    elif category_slug in ['property-inspection-assessment', 'inspection']:
        return property_inspection_view(request)
    elif category_slug in ['government-approvals-compliance', 'government-policies']:
        return government_approvals_view(request)
    elif category_slug in ['property-documentation', 'documentation-assistance']:
        return property_documentation_view(request)
    elif category_slug in ['legal-registration-coordination', 'legal']:
        return legal_coordination_view(request)
    elif category_slug in ['repair-restoration-maintenance', 'repairs']:
        return repair_maintenance_view(request)
    elif category_slug in ['interior-remodeling', 'interior']:
        return interior_remodeling_view(request)
    elif category_slug in ['project-management', 'pmc']:
        return project_management_view(request)

    cat = get_object_or_404(ServiceCategory, slug=category_slug)
    related_guides = BlogPost.objects.filter(status='published')[:3]
    return render(request, 'services/service_home.html', {'category': cat, 'related_guides': related_guides})


