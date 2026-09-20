from django.core.management.base import BaseCommand
from services.models import ServiceCategory, Service
from projects.models import ProjectCategory, Project

class Command(BaseCommand):
    help = 'Seeds initial Services and Projects data'

    def handle(self, *args, **kwargs):
        # 1. Project Categories & Projects
        pcat_res, _ = ProjectCategory.objects.get_or_create(name='Residential Construction', defaults={'slug': 'residential-construction'})
        pcat_renov, _ = ProjectCategory.objects.get_or_create(name='Flat & Apartment Renovation', defaults={'slug': 'flat-renovation'})
        pcat_demol, _ = ProjectCategory.objects.get_or_create(name='Demolition & Redevelopment', defaults={'slug': 'demolition-redevelopment'})
        pcat_comm, _ = ProjectCategory.objects.get_or_create(name='Commercial Projects', defaults={'slug': 'commercial-projects'})

        Project.objects.get_or_create(
            slug='jubilee-hills-luxury-villa',
            defaults={
                'title': 'Jubilee Hills Luxury Villa Construction',
                'category': pcat_res,
                'location': 'Jubilee Hills, Hyderabad',
                'project_type': 'Custom 5BHK Contemporary Villa',
                'client_type': 'Private Resident',
                'project_status': 'completed',
                'duration': '14 Months',
                'built_up_area': '6,500 sq.ft',
                'overview': 'Complete turnkey construction of a contemporary luxury villa with cantilevered balconies, custom double-height living foyer, and integrated solar energy grid.',
                'scope_of_work': 'Architectural planning, soil core testing, isolated footing casting, RCC superstructure, MEP rough-ins, Italian marble flooring, and smart home automation.',
                'challenges': 'Steep rocky terrain requiring controlled rock splitting and customized retaining wall engineering.',
                'solutions': 'Tiered foundation design with stepped RCC retaining walls and sub-surface drainage channels.',
                'featured': True,
                'published': True,
            }
        )

        Project.objects.get_or_create(
            slug='banjara-hills-apartment-renovation',
            defaults={
                'title': '25-Year-Old 3BHK Flat Complete Renovation',
                'category': pcat_renov,
                'location': 'Banjara Hills, Hyderabad',
                'project_type': 'Complete Resale Flat Remodeling',
                'client_type': 'Family Homeowner',
                'project_status': 'completed',
                'duration': '8 Weeks',
                'built_up_area': '2,400 sq.ft',
                'overview': 'Total modernization of an aging 3BHK resale flat. Stripping legacy plumbing, open-concept living transformation, and bathroom waterproofing.',
                'scope_of_work': 'Removal of non-bearing brick partitions, complete CPVC plumbing replacement, 3-phase electrical rewiring, designer false ceilings, and PU waterproof coatings.',
                'challenges': 'Severe concealed plumbing corrosion and chronic bathroom floor dampness affecting the lower flat.',
                'solutions': 'Complete core re-piping, dual-layer polyurethane waterproofing with 72-hour flood testing, and lightweight acoustic partition framing.',
                'featured': True,
                'published': True,
            }
        )

        Project.objects.get_or_create(
            slug='hitech-city-commercial-redevelopment',
            defaults={
                'title': 'Commercial Complex Demolition & Rebuild',
                'category': pcat_demol,
                'location': 'HITEC City, Hyderabad',
                'project_type': 'Demolition & Commercial Reconstruction',
                'client_type': 'Commercial Landowner',
                'project_status': 'completed',
                'duration': '18 Months',
                'built_up_area': '18,000 sq.ft',
                'overview': 'Controlled razing of an obsolete 2-story commercial structure and turnkey reconstruction of a 5-story modern office building.',
                'scope_of_work': 'Municipal demolition permits, mechanical diamond saw cutting, zero-vibration dismantling, foundation excavation, and multi-floor commercial execution.',
                'challenges': 'High-density adjoining buildings and active vehicular traffic requiring stringent dust and noise mitigation.',
                'solutions': 'High-reach excavator dismantling with acoustic sound curtains, continuous mist spray dust suppression, and night-shift debris hauling.',
                'featured': True,
                'published': True,
            }
        )

        self.stdout.write(self.style.SUCCESS("Seeded sample projects successfully!"))
