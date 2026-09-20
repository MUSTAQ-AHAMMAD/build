from django.db import models

class WebsiteSettings(models.Model):
    site_name = models.CharField(max_length=150, default="BUILD+ Construction & Property Services")
    tagline = models.CharField(max_length=255, default="Build Better. Renovate Smarter. Rebuild with Confidence.")
    primary_phone = models.CharField(max_length=50, default="+91 98765 43210")
    whatsapp_number = models.CharField(max_length=50, default="+91 98765 43210")
    primary_email = models.EmailField(default="contact@buildplus.com")
    office_address = models.TextField(default="Suite 402, Builders Tower, Financial District, Hyderabad, India")
    facebook_url = models.URLField(blank=True, default="https://facebook.com")
    instagram_url = models.URLField(blank=True, default="https://instagram.com")
    linkedin_url = models.URLField(blank=True, default="https://linkedin.com")
    years_experience = models.PositiveIntegerField(default=18)
    projects_completed = models.PositiveIntegerField(default=450)
    happy_clients = models.PositiveIntegerField(default=620)
    service_cities = models.CharField(max_length=255, default="Hyderabad, Bangalore, Chennai, Vijayawada, Vizag")
    meta_description = models.TextField(default="Premier construction, flat and apartment renovation, demolition, reconstruction, property redevelopment and NRI property management services.")
    meta_keywords = models.CharField(max_length=255, default="construction, flat renovation, apartment renovation, demolition, reconstruction, redevelopment, NRI property services")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website Settings"
        verbose_name_plural = "Website Settings"

    def __str__(self):
        return self.site_name

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    client_title = models.CharField(max_length=150, help_text="e.g. 3BHK Flat Owner, Jubilee Hills or NRI Property Investor, USA")
    service_rendered = models.CharField(max_length=100, default="Complete Flat Renovation")
    feedback = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    is_featured = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.service_rendered}"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('construction', 'Construction'),
        ('renovation', 'Flat & Apartment Renovation'),
        ('demolition', 'Demolition & Site Services'),
        ('reconstruction', 'Reconstruction & Rebuilding'),
        ('redevelopment', 'Property Redevelopment'),
        ('nri', 'NRI Property Services'),
        ('finance', 'Construction & Renovation Loans'),
    ]
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']

    def __str__(self):
        return f"{self.name} ({self.role})"
