import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

class LeadSource(models.Model):
    """Lead Acquisition Sources (Website, WhatsApp, Google Ads, Referrals, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Lead Source'
        verbose_name_plural = 'Lead Sources'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Lead(models.Model):
    """Core CRM Lead & Project Enquiry Model"""

    CUSTOMER_TYPES = [
        ('individual', 'Individual'),
        ('property_owner', 'Property Owner'),
        ('builder', 'Builder'),
        ('developer', 'Developer'),
        ('investor', 'Investor'),
        ('nri', 'NRI'),
        ('company', 'Company / Corporate'),
        ('agent', 'Agent / Broker'),
        ('other', 'Other'),
    ]

    PREFERRED_CONTACT_METHODS = [
        ('phone', 'Phone Call'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('in_person', 'In-Person Meeting'),
    ]

    PROPERTY_TYPES = [
        ('independent_house', 'Independent House'),
        ('flat', 'Flat'),
        ('apartment', 'Apartment Building'),
        ('villa', 'Villa'),
        ('residential_building', 'Residential Building'),
        ('commercial_building', 'Commercial Building'),
        ('office', 'Office Space'),
        ('shop', 'Retail Shop / Showroom'),
        ('commercial_complex', 'Commercial Complex'),
        ('industrial_property', 'Industrial Property'),
        ('land', 'Plot / Land'),
        ('other', 'Other'),
    ]

    SERVICE_CATEGORIES = [
        ('construction', 'Construction Services'),
        ('renovation', 'Flat & Apartment Renovation'),
        ('demolition', 'Demolition Services'),
        ('reconstruction', 'Reconstruction & Rebuilding'),
        ('redevelopment', 'Property Redevelopment'),
        ('property_land', 'Property & Land Advisory'),
        ('nri_services', 'NRI Property Services'),
        ('finance', 'Construction & Renovation Finance'),
    ]

    SERVICE_TYPES = [
        # Construction
        ('independent_house_construction', 'Independent House Construction'),
        ('residential_construction', 'Residential Construction'),
        ('apartment_construction', 'Apartment Construction'),
        ('villa_construction', 'Villa Construction'),
        ('commercial_construction', 'Commercial Construction'),
        ('industrial_construction', 'Industrial / Structural Construction'),

        # Renovation
        ('flat_renovation', 'Flat Renovation'),
        ('apartment_renovation', 'Apartment Renovation'),
        ('old_flat_renovation', 'Old Flat Renovation'),
        ('damaged_flat_renovation', 'Damaged Flat Renovation'),
        ('interior_renovation', 'Interior Renovation'),
        ('structural_renovation', 'Structural Renovation'),
        ('kitchen_renovation', 'Kitchen Renovation'),
        ('bathroom_renovation', 'Bathroom Renovation'),
        ('common_area_renovation', 'Common Area Renovation'),

        # Demolition
        ('building_demolition', 'Building Demolition'),
        ('flat_demolition', 'Flat Demolition'),
        ('apartment_demolition', 'Apartment Demolition'),
        ('partial_demolition', 'Partial Demolition'),
        ('complete_demolition', 'Complete Demolition'),
        ('damaged_building_demolition', 'Damaged Building Demolition'),
        ('site_clearing', 'Site Clearing'),

        # Reconstruction
        ('partial_reconstruction', 'Partial Reconstruction'),
        ('complete_reconstruction', 'Complete Reconstruction'),
        ('structural_reconstruction', 'Structural Reconstruction'),
        ('reconstruction_after_demolition', 'Reconstruction After Demolition'),

        # Redevelopment
        ('property_redevelopment', 'Property Redevelopment'),
        ('apartment_redevelopment', 'Apartment Redevelopment'),
        ('old_building_redevelopment', 'Old Building Redevelopment'),
        ('multi_unit_redevelopment', 'Multi-Unit Redevelopment'),
        ('demolition_plus_reconstruction', 'Demolition + Reconstruction'),

        # Property & Land
        ('property_buying', 'Property Buying'),
        ('property_selling', 'Property Selling'),
        ('land_buying', 'Land Buying'),
        ('land_selling', 'Land Selling'),
        ('property_inspection', 'Property Inspection'),
        ('property_management', 'Property Management'),
        ('land_management', 'Land Management'),

        # NRI Services
        ('nri_property_management', 'NRI Property Management'),
        ('nri_land_management', 'NRI Land Management'),
        ('nri_property_inspection', 'NRI Property Inspection'),
        ('nri_construction_supervision', 'NRI Construction Supervision'),
        ('nri_renovation_supervision', 'NRI Renovation Supervision'),
        ('nri_demolition_supervision', 'NRI Demolition Supervision'),
        ('nri_reconstruction_supervision', 'NRI Reconstruction Supervision'),
        ('nri_property_buying', 'NRI Property Buying'),
        ('nri_property_selling', 'NRI Property Selling'),
        ('nri_documentation_assistance', 'NRI Documentation Assistance'),

        # Finance
        ('construction_loan', 'Construction Loan'),
        ('home_building_loan', 'Home / Building Loan'),
        ('renovation_finance', 'Renovation Finance'),
        ('property_finance', 'Property Finance'),
        ('loan_documentation', 'Loan Documentation'),
    ]

    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONTACTED', 'Contacted'),
        ('QUALIFIED', 'Qualified'),
        ('SITE_VISIT', 'Site Visit'),
        ('REQUIREMENT_CONFIRMED', 'Requirement Confirmed'),
        ('ESTIMATE_PREPARED', 'Estimate Prepared'),
        ('PROPOSAL_SENT', 'Proposal Sent'),
        ('NEGOTIATION', 'Negotiation'),
        ('WON', 'Won'),
        ('LOST', 'Lost'),
        ('ON_HOLD', 'On Hold'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    LOST_REASONS = [
        ('budget', 'Budget / Price too High'),
        ('competitor', 'Chosen Competitor'),
        ('cancelled', 'Customer Cancelled Project'),
        ('location', 'Location Outside Service Scope'),
        ('not_interested', 'Not Interested / Invalid Lead'),
        ('timeline', 'Timeline Mismatch'),
        ('unreachable', 'Could Not Contact / No Response'),
        ('duplicate', 'Duplicate Enquiry'),
        ('other', 'Other Reason'),
    ]

    # Identifier
    lead_id = models.CharField(max_length=32, unique=True, editable=False, db_index=True)

    # Customer Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=25, db_index=True)
    alternate_phone = models.CharField(max_length=25, blank=True)
    email = models.EmailField(blank=True, db_index=True)
    whatsapp_number = models.CharField(max_length=25, blank=True)
    preferred_contact_method = models.CharField(max_length=20, choices=PREFERRED_CONTACT_METHODS, default='phone')
    customer_type = models.CharField(max_length=30, choices=CUSTOMER_TYPES, default='individual')

    # Project Information
    service_category = models.CharField(max_length=40, choices=SERVICE_CATEGORIES, default='construction', db_index=True)
    service_type = models.CharField(max_length=60, choices=SERVICE_TYPES, default='residential_construction', db_index=True)
    property_type = models.CharField(max_length=40, choices=PROPERTY_TYPES, default='independent_house')
    property_location = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, default='Hyderabad', db_index=True)
    area_locality = models.CharField(max_length=120, blank=True)
    approximate_property_area = models.CharField(max_length=80, blank=True, help_text="e.g. 2,400 sq.ft or 300 sq.yds")
    unit = models.CharField(max_length=20, default='sq.ft')
    project_description = models.TextField(blank=True)

    # Commercial Information
    estimated_budget = models.CharField(max_length=100, blank=True, help_text="Customer stated budget")
    budget_range = models.CharField(max_length=100, blank=True)
    expected_project_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, help_text="Pipeline value in ₹")
    final_project_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, help_text="Closed Won value in ₹")
    expected_closing_date = models.DateField(null=True, blank=True)
    won_date = models.DateField(null=True, blank=True)
    lost_reason = models.CharField(max_length=40, choices=LOST_REASONS, blank=True)
    lost_notes = models.TextField(blank=True)
    on_hold_reason = models.TextField(blank=True)

    # CRM Pipeline & Assignment
    lead_source = models.ForeignKey(LeadSource, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    lead_source_text = models.CharField(max_length=100, default='Website', blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_crm_leads')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM', db_index=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='NEW', db_index=True)
    next_follow_up_date = models.DateTimeField(null=True, blank=True, db_index=True)

    # Soft Delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_crm_leads')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['city', 'service_category']),
        ]

    def __str__(self):
        return f"[{self.lead_id}] {self.full_name} ({self.get_service_type_display()})"

    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.first_name

    @property
    def is_overdue(self):
        if self.next_follow_up_date and self.status not in ['WON', 'LOST']:
            return self.next_follow_up_date < timezone.now()
        return False

    @property
    def status_badge_class(self):
        badges = {
            'NEW': 'bg-primary',
            'CONTACTED': 'bg-info text-dark',
            'QUALIFIED': 'bg-secondary',
            'SITE_VISIT': 'bg-warning text-dark',
            'REQUIREMENT_CONFIRMED': 'bg-primary',
            'ESTIMATE_PREPARED': 'bg-info text-dark',
            'PROPOSAL_SENT': 'bg-indigo text-white',
            'NEGOTIATION': 'bg-dark text-white',
            'WON': 'bg-success',
            'LOST': 'bg-danger',
            'ON_HOLD': 'bg-light text-dark border',
        }
        return badges.get(self.status, 'bg-secondary')

    @property
    def priority_badge_class(self):
        badges = {
            'LOW': 'bg-light text-muted border',
            'MEDIUM': 'bg-info-subtle text-info-emphasis border',
            'HIGH': 'bg-warning text-dark',
            'URGENT': 'bg-danger text-white',
        }
        return badges.get(self.priority, 'bg-secondary')

    def save(self, *args, **kwargs):
        if not self.lead_id:
            today_str = timezone.now().strftime('%Y%m%d')
            random_num = random.randint(1000, 9999)
            self.lead_id = f"LEAD-{today_str}-{random_num}"
            # Ensure unique
            while Lead.objects.filter(lead_id=self.lead_id).exists():
                random_num = random.randint(1000, 9999)
                self.lead_id = f"LEAD-{today_str}-{random_num}"
        
        if not self.whatsapp_number and self.phone:
            self.whatsapp_number = self.phone

        super().save(*args, **kwargs)


class FollowUp(models.Model):
    """Scheduled & Logged Customer Communications"""

    FOLLOWUP_TYPES = [
        ('phone', 'Phone Call'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('meeting', 'In-Person Meeting'),
        ('site_visit', 'Site Visit Follow-up'),
        ('video_call', 'Video Call'),
        ('other', 'Other'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='follow_ups')
    follow_up_date = models.DateField()
    follow_up_time = models.TimeField(null=True, blank=True)
    follow_up_type = models.CharField(max_length=30, choices=FOLLOWUP_TYPES, default='phone')
    subject = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    outcome = models.TextField(blank=True, help_text="What happened during communication")
    next_follow_up_date = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_follow_ups')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['completed', 'follow_up_date', 'follow_up_time']
        verbose_name = 'Follow-up'
        verbose_name_plural = 'Follow-ups'

    def __str__(self):
        return f"{self.get_follow_up_type_display()} with {self.lead.full_name} on {self.follow_up_date}"


class SiteVisit(models.Model):
    """On-Site Technical Engineering Inspections"""

    VISIT_STATUSES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='site_visits')
    site_address = models.CharField(max_length=255)
    visit_date = models.DateField()
    visit_time = models.TimeField(null=True, blank=True)
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_site_visits')
    site_contact = models.CharField(max_length=150, blank=True, help_text="On-site contact person & phone")
    property_type = models.CharField(max_length=100, blank=True)
    site_condition = models.TextField(blank=True, help_text="Existing structure age, dampness, structural cracks, access roads")
    requirements = models.TextField(blank=True, help_text="Client specific requirements gathered on-site")
    measurements = models.TextField(blank=True, help_text="Field dimensions, built-up area check, column spans")
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=VISIT_STATUSES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visit_date', '-visit_time']
        verbose_name = 'Site Visit'
        verbose_name_plural = 'Site Visits'

    def __str__(self):
        return f"Site Visit for {self.lead.full_name} on {self.visit_date} ({self.get_status_display()})"


class Estimate(models.Model):
    """Cost Estimates & Quotation Proposals for CRM Tracking"""

    ESTIMATE_STATUSES = [
        ('draft', 'Draft'),
        ('prepared', 'Prepared'),
        ('sent', 'Sent to Client'),
        ('under_discussion', 'Under Discussion / Revision'),
        ('approved', 'Approved / Accepted'),
        ('rejected', 'Rejected'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='estimates')
    estimate_number = models.CharField(max_length=50, unique=True)
    estimate_date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255, help_text="e.g. 3BHK Turnkey Renovation BOQ Rev-1")
    estimated_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, help_text="Subtotal in ₹")
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, help_text="GST / Tax in ₹")
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, help_text="Grand Total in ₹")
    valid_until = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=ESTIMATE_STATUSES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-estimate_date', '-created_at']
        verbose_name = 'Estimate / Proposal'
        verbose_name_plural = 'Estimates & Proposals'

    def __str__(self):
        return f"{self.estimate_number} - {self.lead.full_name} (₹{self.total_amount:,.2f})"

    def save(self, *args, **kwargs):
        if not self.estimate_number:
            year_str = timezone.now().strftime('%Y')
            random_num = random.randint(100, 999)
            self.estimate_number = f"EST-{year_str}-{random_num}"
            while Estimate.objects.filter(estimate_number=self.estimate_number).exists():
                random_num = random.randint(100, 999)
                self.estimate_number = f"EST-{year_str}-{random_num}"
        
        if self.estimated_amount and not self.total_amount:
            self.total_amount = self.estimated_amount + (self.tax_amount or 0)
            
        super().save(*args, **kwargs)


class LeadNote(models.Model):
    """Staff Internal Discussion Notes"""
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead Note'
        verbose_name_plural = 'Lead Notes'

    def __str__(self):
        return f"Note on {self.lead.lead_id} by {self.created_by}"


class LeadActivity(models.Model):
    """Chronological CRM Activity Timeline Log"""

    ACTIVITY_TYPES = [
        ('created', 'Lead Created'),
        ('assigned', 'Staff Assigned'),
        ('status_changed', 'Status Updated'),
        ('followup_added', 'Follow-up Added'),
        ('followup_completed', 'Follow-up Completed'),
        ('sitevisit_scheduled', 'Site Visit Scheduled'),
        ('sitevisit_completed', 'Site Visit Completed'),
        ('estimate_created', 'Estimate Created'),
        ('proposal_sent', 'Proposal Sent'),
        ('marked_won', 'Marked Won'),
        ('marked_lost', 'Marked Lost'),
        ('note_added', 'Note Added'),
        ('restored', 'Lead Restored'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead Activity'
        verbose_name_plural = 'Lead Activities'

    def __str__(self):
        return f"{self.title} on {self.lead.lead_id}"
