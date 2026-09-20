from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import WebsiteSettings, Testimonial, FAQ, TeamMember
from .forms import CMSLoginForm, WebsiteSettingsForm
from blog.models import BlogPost, BlogCategory
from enquiries.models import Enquiry
from projects.models import Project
import logging

logger = logging.getLogger(__name__)

def home_view(request):
    """Public Home Page with all core highlights, service shortcuts, projects, and featured blog insights"""
    featured_blogs = BlogPost.objects.filter(status='published', featured=True)[:3]
    if not featured_blogs.exists():
        featured_blogs = BlogPost.objects.filter(status='published')[:3]

    testimonials = Testimonial.objects.filter(is_featured=True)[:4]
    faqs = FAQ.objects.filter(is_published=True)[:6]
    featured_projects = Project.objects.filter(published=True, featured=True)[:5]

    context = {
        'featured_blogs': featured_blogs,
        'testimonials': testimonials,
        'faqs': faqs,
        'featured_projects': featured_projects,
    }
    return render(request, 'home.html', context)


def about_view(request):
    """Public About Us page"""
    team_members = TeamMember.objects.all()
    return render(request, 'about.html', {'team_members': team_members})


def how_we_work_view(request):
    """Public How We Work & Process page"""
    return render(request, 'how_we_work.html')


def faqs_view(request):
    """Public FAQs directory page"""
    category_filter = request.GET.get('category', '')
    faqs = FAQ.objects.filter(is_published=True)
    if category_filter:
        faqs = faqs.filter(category=category_filter)
    
    return render(request, 'faqs.html', {'faqs': faqs, 'category_filter': category_filter, 'categories': FAQ.CATEGORY_CHOICES})


def privacy_view(request):
    """Privacy Policy page"""
    return render(request, 'privacy.html')


def terms_view(request):
    """Terms & Conditions page"""
    return render(request, 'terms.html')


def disclaimer_view(request):
    """Disclaimer page"""
    return render(request, 'disclaimer.html')


def cookie_policy_view(request):
    """Cookie Policy page"""
    return render(request, 'cookie_policy.html')


def sitemap_xml(request):
    """Dynamically generates search-engine compliant sitemap.xml"""
    from django.http import HttpResponse
    from django.utils import timezone
    published_blogs = BlogPost.objects.filter(status='published')
    categories = BlogCategory.objects.filter(status='active')
    projects = Project.objects.filter(published=True)

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url><loc>https://buildplus.com/</loc><priority>1.0</priority><changefreq>daily</changefreq></url>',
        '  <url><loc>https://buildplus.com/about/</loc><priority>0.8</priority></url>',
        '  <url><loc>https://buildplus.com/how-we-work/</loc><priority>0.8</priority></url>',
        '  <url><loc>https://buildplus.com/construction/</loc><priority>0.9</priority></url>',
        '  <url><loc>https://buildplus.com/renovation/</loc><priority>0.9</priority></url>',
        '  <url><loc>https://buildplus.com/demolition-reconstruction/</loc><priority>0.9</priority></url>',
        '  <url><loc>https://buildplus.com/redevelopment/</loc><priority>0.9</priority></url>',
        '  <url><loc>https://buildplus.com/property-land/</loc><priority>0.8</priority></url>',
        '  <url><loc>https://buildplus.com/nri-services/</loc><priority>0.9</priority></url>',
        '  <url><loc>https://buildplus.com/construction-finance/</loc><priority>0.8</priority></url>',
        '  <url><loc>https://buildplus.com/projects/</loc><priority>0.8</priority></url>',
        '  <url><loc>https://buildplus.com/blog/</loc><priority>0.9</priority><changefreq>daily</changefreq></url>',
        '  <url><loc>https://buildplus.com/faqs/</loc><priority>0.7</priority></url>',
        '  <url><loc>https://buildplus.com/contact/</loc><priority>0.8</priority></url>',
        '  <url><loc>https://buildplus.com/request-site-visit/</loc><priority>0.9</priority></url>',
    ]

    for blog in published_blogs:
        lastmod = blog.updated_at.strftime('%Y-%m-%d')
        xml_lines.append(f'  <url><loc>https://buildplus.com/blog/{blog.slug}/</loc><lastmod>{lastmod}</lastmod><priority>0.8</priority></url>')

    for cat in categories:
        xml_lines.append(f'  <url><loc>https://buildplus.com/blog/?category={cat.slug}</loc><priority>0.7</priority></url>')

    for p in projects:
        xml_lines.append(f'  <url><loc>https://buildplus.com/projects/{p.slug}/</loc><priority>0.7</priority></url>')

    xml_lines.append('</urlset>')
    return HttpResponse('\n'.join(xml_lines), content_type='application/xml')


def robots_txt(request):
    """Generates standard robots.txt"""
    from django.http import HttpResponse
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /cms/",
        "Disallow: /admin/",
        "",
        "Sitemap: https://buildplus.com/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def contact_view(request):
    """Public Contact Page with form submission to Enquiry model"""
    success = False
    enquiry_number = None

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        city_location = request.POST.get('city_location', '').strip()
        enquiry_type = request.POST.get('enquiry_type', 'flat_renovation')
        property_type = request.POST.get('property_type', '').strip()
        approximate_area = request.POST.get('approximate_area', '').strip()
        message = request.POST.get('message', '').strip()
        site_visit_requested = request.POST.get('site_visit_requested') == 'on'

        if full_name and phone_number and city_location and message:
            try:
                enquiry = Enquiry.objects.create(
                    full_name=full_name, phone_number=phone_number, email=email,
                    city_location=city_location, enquiry_type=enquiry_type,
                    property_type=property_type, approximate_area=approximate_area,
                    message=message, site_visit_requested=site_visit_requested, status='NEW',
                )
                success = True
                enquiry_number = enquiry.enquiry_number
            except Exception as e:
                logger.error(f"Contact form error: {e}")
                messages.error(request, "Something went wrong. Please try again or call us directly.")
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'contact.html', {
        'success': success, 'enquiry_number': enquiry_number,
        'enquiry_types': Enquiry.ENQUIRY_TYPE_CHOICES,
    })


def consultation_view(request):
    """Get Free Consultation page — premium conversion form"""
    success = False
    enquiry_number = None

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        city_location = request.POST.get('city_location', '').strip()
        enquiry_type = request.POST.get('enquiry_type', 'construction')
        property_type = request.POST.get('property_type', '').strip()
        approximate_area = request.POST.get('approximate_area', '').strip()
        budget_range = request.POST.get('budget_range', '').strip()
        timeline = request.POST.get('timeline', '').strip()
        additional = request.POST.get('additional_requirement', '').strip()
        parts = []
        if budget_range: parts.append(f"Budget: {budget_range}")
        if timeline: parts.append(f"Timeline: {timeline}")
        if additional: parts.append(f"Notes: {additional}")
        message = '\n'.join(parts) or 'Free consultation request via website'

        if full_name and phone_number and city_location:
            try:
                enquiry = Enquiry.objects.create(
                    full_name=full_name, phone_number=phone_number, email=email,
                    city_location=city_location, enquiry_type=enquiry_type,
                    property_type=property_type, approximate_area=approximate_area,
                    message=message, status='NEW',
                )
                success = True
                enquiry_number = enquiry.enquiry_number
            except Exception as e:
                logger.error(f"Consultation form error: {e}")
                messages.error(request, "Something went wrong. Please try again or call us directly.")
        else:
            messages.error(request, "Please fill in Name, Phone and Location to continue.")

    return render(request, 'consultation.html', {
        'success': success, 'enquiry_number': enquiry_number,
        'enquiry_types': Enquiry.ENQUIRY_TYPE_CHOICES,
    })


# ==============================================================================
# CMS AUTHENTICATION & GLOBAL DASHBOARD
# ==============================================================================

def cms_login(request):
    """CMS Portal Login View"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('core:cms_dashboard')

    if request.method == 'POST':
        form = CMSLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect(request.GET.get('next') or 'core:cms_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CMSLoginForm()

    return render(request, 'cms/login.html', {'form': form})


def cms_logout(request):
    """CMS Portal Logout View"""
    logout(request)
    messages.info(request, "You have been logged out of the CMS portal.")
    return redirect('core:cms_login')


@login_required(login_url='/cms/login/')
@user_passes_test(lambda u: u.is_staff)
def cms_dashboard(request):
    """Central CMS Command Dashboard"""
    context = {
        'total_blogs': BlogPost.objects.count(),
        'published_blogs': BlogPost.objects.filter(status='published').count(),
        'draft_blogs': BlogPost.objects.filter(status='draft').count(),
        'total_categories': BlogCategory.objects.count(),
        'new_enquiries': Enquiry.objects.filter(status='NEW').count(),
        'total_enquiries': Enquiry.objects.count(),
        'total_projects': Project.objects.count(),
        'recent_enquiries': Enquiry.objects.all()[:5],
        'recent_blogs': BlogPost.objects.select_related('category').order_by('-created_at')[:5],
    }
    return render(request, 'cms/dashboard.html', context)


@login_required(login_url='/cms/login/')
@user_passes_test(lambda u: u.is_staff)
def cms_settings(request):
    """Global Website Settings CMS Editor"""
    settings_obj = WebsiteSettings.load()
    if request.method == 'POST':
        form = WebsiteSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Website Settings updated successfully.")
            return redirect('core:cms_settings')
        else:
            messages.error(request, "Error updating settings. Please review form.")
    else:
        form = WebsiteSettingsForm(instance=settings_obj)

    return render(request, 'cms/settings.html', {'form': form, 'settings': settings_obj})


# ==============================================================================
# CUSTOM ERROR HANDLERS
# ==============================================================================

def custom_404_view(request, exception=None):
    """Custom branded 404 Not Found Page"""
    return render(request, '404.html', status=404)


def custom_500_view(request):
    """Custom branded 500 Server Error Page"""
    return render(request, '500.html', status=500)


def custom_403_view(request, exception=None):
    """Custom branded 403 Access Denied Page"""
    return render(request, '403.html', status=403)


def custom_400_view(request, exception=None):
    """Custom branded 400 Bad Request Page"""
    return render(request, '400.html', status=400)

