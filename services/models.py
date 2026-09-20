from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class ServiceCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    short_description = models.TextField(blank=True)
    hero_title = models.CharField(max_length=200, blank=True)
    hero_subtitle = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="⌂", help_text="Emoji or icon symbol")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.TextField(max_length=500)
    full_description = models.TextField(blank=True)
    service_icon = models.CharField(max_length=50, default="✦")
    benefits = models.TextField(blank=True, help_text="One benefit per line or HTML")
    process_steps = models.TextField(blank=True, help_text="One step per line or HTML")
    hero_image = models.ImageField(upload_to='services/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    seo_title = models.CharField(max_length=180, blank=True)
    seo_description = models.CharField(max_length=255, blank=True)
    seo_keywords = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
