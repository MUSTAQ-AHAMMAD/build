from django.contrib import admin
from .models import Enquiry

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'enquiry_type', 'phone_number', 'city_location', 'status', 'site_visit_requested', 'created_at')
    list_filter = ('enquiry_type', 'status', 'site_visit_requested', 'created_at')
    search_fields = ('full_name', 'phone_number', 'email', 'city_location', 'message')
    date_hierarchy = 'created_at'
