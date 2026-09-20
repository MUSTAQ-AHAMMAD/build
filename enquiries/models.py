from django.db import models

class Enquiry(models.Model):
    ENQUIRY_TYPE_CHOICES = [
        ('construction', 'New Construction (House, Villa, Commercial)'),
        ('flat_renovation', 'Flat & Apartment Renovation'),
        ('apartment_renovation', 'Multi-Unit Apartment Renovation'),
        ('demolition', 'Building / Flat Demolition & Clearing'),
        ('reconstruction', 'Reconstruction & Rebuilding'),
        ('redevelopment', 'Property & Society Redevelopment'),
        ('property_land', 'Property & Land Advisory'),
        ('nri_services', 'NRI Property Support & Supervision'),
        ('construction_loan', 'Construction & Renovation Loan Assistance'),
        ('site_visit', 'Site Visit & Inspection Request'),
    ]

    STATUS_CHOICES = [
        ('NEW', 'New / Unread'),
        ('CONTACTED', 'Contacted / In Discussion'),
        ('SITE_VISIT', 'Site Visit Scheduled'),
        ('ESTIMATE', 'Estimate / BOQ Shared'),
        ('PROPOSAL', 'Proposal Under Review'),
        ('NEGOTIATION', 'In Negotiation'),
        ('CONVERTED', 'Converted to Active Project'),
        ('CLOSED', 'Closed / Not Feasible'),
    ]

    enquiry_number = models.CharField(max_length=30, unique=True, blank=True, db_index=True)
    enquiry_type = models.CharField(max_length=30, choices=ENQUIRY_TYPE_CHOICES, default='flat_renovation')
    full_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    city_location = models.CharField(max_length=150, help_text="e.g. Jubilee Hills, Hyderabad")
    property_type = models.CharField(max_length=100, blank=True, help_text="e.g. 3BHK Resale Flat, G+2 Independent Building, Plot")
    approximate_area = models.CharField(max_length=60, blank=True, help_text="e.g. 1,800 sq.ft or 300 sq.yds")
    message = models.TextField(help_text="Describe your property requirement, existing condition, or project goals")
    site_visit_requested = models.BooleanField(default=False)
    preferred_date = models.DateField(blank=True, null=True)
    
    # Internal CMS workflow management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    internal_notes = models.TextField(blank=True, help_text="Internal notes for team and follow-up history")
    assigned_engineer = models.CharField(max_length=100, blank=True, default="Unassigned")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Enquiry / Lead"
        verbose_name_plural = "Enquiries & Leads"

    def __str__(self):
        return f"[{self.enquiry_number or 'CN'}] {self.full_name} ({self.get_enquiry_type_display()})"

    def save(self, *args, **kwargs):
        if not self.enquiry_number:
            import random
            from django.utils import timezone
            year = timezone.now().strftime('%Y')
            random_num = random.randint(100000, 999999)
            self.enquiry_number = f"CN-{year}-{random_num}"
            while Enquiry.objects.filter(enquiry_number=self.enquiry_number).exclude(pk=self.pk).exists():
                random_num = random.randint(100000, 999999)
                self.enquiry_number = f"CN-{year}-{random_num}"
        super().save(*args, **kwargs)
