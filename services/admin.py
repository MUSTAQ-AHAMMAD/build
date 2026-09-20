from django.contrib import admin
from .models import ServiceCategory, Service

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'featured', 'published', 'display_order')
    list_filter = ('category', 'featured', 'published')
    search_fields = ('name', 'short_description', 'full_description')
    prepopulated_fields = {'slug': ('name',)}
