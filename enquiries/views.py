from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Enquiry
from .forms import PublicEnquiryForm, CMSEnquiryUpdateForm
from crm.models import Lead, LeadSource, SiteVisit, LeadActivity

def sync_enquiry_to_crm(enquiry):
    """Bridge public website enquiry into the CRM Lead model."""
    try:
        source, _ = LeadSource.objects.get_or_create(name='Website', defaults={'slug': 'website'})
        
        # Map enquiry type to CRM service category and type
        type_mapping = {
            'construction': ('construction', 'residential_construction'),
            'flat_renovation': ('renovation', 'flat_renovation'),
            'demolition': ('demolition', 'building_demolition'),
            'redevelopment': ('redevelopment', 'property_redevelopment'),
            'property_management': ('property_land', 'property_management'),
            'nri_services': ('nri_services', 'nri_property_management'),
            'construction_loan': ('finance', 'construction_loan'),
            'site_visit': ('renovation', 'flat_renovation'),
            'other': ('construction', 'residential_construction'),
        }
        sec_cat, sec_type = type_mapping.get(enquiry.enquiry_type, ('construction', 'residential_construction'))
        
        # Determine initial status
        initial_status = 'SITE_VISIT' if enquiry.site_visit_requested else 'NEW'

        # Create or update CRM lead
        names = enquiry.full_name.strip().split(' ', 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ''

        crm_lead = Lead.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone=enquiry.phone_number,
            email=enquiry.email or '',
            city=enquiry.city_location or 'Hyderabad',
            property_location=enquiry.city_location or '',
            property_type='flat' if 'flat' in (enquiry.property_type or '').lower() else 'independent_house',
            approximate_property_area=enquiry.approximate_area or '',
            project_description=enquiry.message or '',
            service_category=sec_cat,
            service_type=sec_type,
            lead_source=source,
            lead_source_text='Website Contact Form',
            status=initial_status,
            priority='HIGH' if enquiry.site_visit_requested else 'MEDIUM',
        )

        # Log Activity
        LeadActivity.objects.create(
            lead=crm_lead,
            activity_type='created',
            title=f"Website Enquiry Received ({enquiry.enquiry_number})",
            description=f"Enquiry Number: {enquiry.enquiry_number}\nEnquiry Type: {enquiry.get_enquiry_type_display()}\nLocation: {enquiry.city_location}\nMessage: {enquiry.message}",
        )

        # If site visit was requested, also create a SiteVisit record
        if enquiry.site_visit_requested:
            SiteVisit.objects.create(
                lead=crm_lead,
                site_address=enquiry.city_location,
                visit_date=timezone.now().date(),
                site_contact=f"{enquiry.full_name} ({enquiry.phone_number})",
                property_type=enquiry.property_type or 'Property Site',
                requirements=enquiry.message or 'Site inspection requested via website form',
                status='scheduled'
            )

        return crm_lead
    except Exception as e:
        # Graceful fallback: do not crash public form if CRM sync has transient issue
        return None


def contact_view(request):
    """Public Contact and Multi-Type Enquiry page"""
    enquiry_type_initial = request.GET.get('type', 'flat_renovation')
    if request.method == 'POST':
        form = PublicEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()
            sync_enquiry_to_crm(enquiry)
            messages.success(
                request,
                f"Thank you, {enquiry.full_name}! Your {enquiry.get_enquiry_type_display()} enquiry has been received. "
                "Our engineering team will contact you shortly."
            )
            return redirect('enquiries:contact')
    else:
        form = PublicEnquiryForm(initial={'enquiry_type': enquiry_type_initial})

    return render(request, 'enquiries/contact.html', {'form': form})


def site_visit_request(request):
    """Dedicated Site Visit & Inspection Request page"""
    if request.method == 'POST':
        form = PublicEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.site_visit_requested = True
            enquiry.save()
            sync_enquiry_to_crm(enquiry)
            messages.success(
                request,
                f"Site Visit Request confirmed! Our technical team will reach out to schedule an on-site property inspection."
            )
            return redirect('enquiries:site_visit')
    else:
        form = PublicEnquiryForm(initial={'enquiry_type': 'site_visit', 'site_visit_requested': True})

    return render(request, 'enquiries/site_visit.html', {'form': form})


# CMS Lead Management Views (Redirect to full CRM)
@login_required(login_url='/cms/login/')
@user_passes_test(lambda u: u.is_staff)
def cms_enquiry_inbox(request):
    """Redirects to the new comprehensive CRM Leads module."""
    return redirect('crm:lead_list')


@login_required(login_url='/cms/login/')
@user_passes_test(lambda u: u.is_staff)
def cms_enquiry_detail(request, pk):
    """Redirects to the new comprehensive CRM Lead Detail profile."""
    return redirect('crm:lead_list')
