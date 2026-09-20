import math
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

class BlogCategory(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Brief description of this category for SEO and public listings")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while BlogCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"{reverse('blog:public_list')}?category={self.slug}"

    @property
    def published_blogs_count(self):
        return self.blogs.filter(status='published').count()

    @property
    def total_blogs_count(self):
        return self.blogs.count()


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    SERVICE_TYPE_CHOICES = [
        ('flat_renovation', 'Flat & Apartment Renovation'),
        ('construction', 'New Construction (Houses & Villas)'),
        ('demolition', 'Building Demolition & Site Clearance'),
        ('reconstruction', 'Reconstruction & Rebuilding'),
        ('redevelopment', 'Property Redevelopment'),
        ('property_land', 'Property & Land Advisory'),
        ('nri_services', 'NRI Property Services'),
        ('construction_loan', 'Construction & Renovation Loans'),
    ]

    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    category = models.ForeignKey(
        BlogCategory, 
        on_delete=models.PROTECT, 
        related_name='blogs',
        help_text="Primary category for this article"
    )
    author = models.CharField(max_length=100, default="BUILD+ Editorial Team")
    short_description = models.TextField(
        max_length=500,
        help_text="Short summary displayed in blog listings and search results (max 500 chars)"
    )
    content = models.TextField(
        help_text="Main blog content with formatted HTML, headings, lists, quotes, and imagery"
    )
    featured_image = models.ImageField(
        upload_to='blog/%Y/%m/',
        blank=True,
        null=True,
        help_text="Hero image for public card listings and blog header (JPG, PNG, WebP)"
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(
        default=False, 
        help_text="Check to display on the Home page Featured Insights carousel"
    )
    published_date = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Date and time when article was published"
    )
    
    # Commercial Service Link (Section 31 of Requirements)
    related_service_type = models.CharField(
        max_length=40,
        choices=SERVICE_TYPE_CHOICES,
        default='flat_renovation',
        help_text="Commercial service to link for contextual high-converting lead generation"
    )

    # SEO Metadata
    seo_title = models.CharField(
        max_length=180, 
        blank=True, 
        help_text="Custom SEO page title tag (defaults to blog title if empty)"
    )
    seo_description = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Custom meta description for search engines (defaults to short description)"
    )
    seo_keywords = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Comma-separated SEO keywords (e.g. flat renovation, old apartment repair)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date', '-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # If status is published and published_date is None, set to current time
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:public_detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        """Estimate reading time in minutes based on 200 words per minute of text content"""
        import re
        clean_text = re.sub(r'<[^>]+>', ' ', self.content)
        word_count = len(clean_text.split())
        return max(1, math.ceil(word_count / 200))

    @property
    def is_published(self):
        return self.status == 'published'

    def get_meta_title(self):
        return self.seo_title.strip() if self.seo_title else self.title

    def get_meta_description(self):
        return self.seo_description.strip() if self.seo_description else self.short_description
