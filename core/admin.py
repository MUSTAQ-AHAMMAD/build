from django.contrib import admin
from .models import WebsiteSettings, Testimonial, FAQ, TeamMember

@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'primary_phone', 'primary_email', 'updated_at')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'service_rendered', 'rating', 'is_featured', 'display_order')
    list_filter = ('is_featured', 'rating')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_published', 'display_order')
    list_filter = ('category', 'is_published')
    search_fields = ('question', 'answer')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'display_order')
