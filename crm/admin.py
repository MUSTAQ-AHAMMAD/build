from django.contrib import admin
from .models import LeadSource, Lead, FollowUp, SiteVisit, Estimate, LeadNote, LeadActivity

class FollowUpInline(admin.TabularInline):
    model = FollowUp
    extra = 0
    fields = ['follow_up_date', 'follow_up_time', 'follow_up_type', 'subject', 'completed', 'assigned_to']


class SiteVisitInline(admin.TabularInline):
    model = SiteVisit
    extra = 0
    fields = ['visit_date', 'visit_time', 'site_address', 'status', 'assigned_staff']


class EstimateInline(admin.TabularInline):
    model = Estimate
    extra = 0
    fields = ['estimate_number', 'estimate_date', 'description', 'total_amount', 'status']


class LeadNoteInline(admin.StackedInline):
    model = LeadNote
    extra = 0
    fields = ['note', 'created_by', 'created_at']
    readonly_fields = ['created_at']


class LeadActivityInline(admin.TabularInline):
    model = LeadActivity
    extra = 0
    fields = ['created_at', 'activity_type', 'title', 'performed_by']
    readonly_fields = ['created_at', 'activity_type', 'title', 'performed_by']


@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['lead_id', 'full_name', 'phone', 'service_category', 'service_type', 'status', 'priority', 'assigned_to', 'expected_project_value', 'created_at']
    list_filter = ['status', 'priority', 'service_category', 'customer_type', 'city', 'lead_source', 'is_deleted']
    search_fields = ['lead_id', 'first_name', 'last_name', 'phone', 'email', 'city', 'property_location', 'company_name']
    readonly_fields = ['lead_id', 'created_at', 'updated_at']
    inlines = [FollowUpInline, SiteVisitInline, EstimateInline, LeadNoteInline, LeadActivityInline]

    fieldsets = (
        ('System Identifier', {
            'fields': ('lead_id', 'status', 'priority', 'assigned_to', 'next_follow_up_date', 'lead_source')
        }),
        ('Customer Details', {
            'fields': (('first_name', 'last_name'), 'company_name', ('phone', 'alternate_phone'), ('email', 'whatsapp_number'), ('customer_type', 'preferred_contact_method'))
        }),
        ('Project Information', {
            'fields': (('service_category', 'service_type'), 'property_type', ('city', 'area_locality'), 'property_location', ('approximate_property_area', 'unit'), 'project_description')
        }),
        ('Commercials', {
            'fields': (('estimated_budget', 'budget_range'), ('expected_project_value', 'final_project_value'), ('expected_closing_date', 'won_date'), ('lost_reason', 'lost_notes'), 'on_hold_reason')
        }),
        ('Soft Deletion State', {
            'classes': ('collapse',),
            'fields': ('is_deleted', 'deleted_at', 'deleted_by')
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ['lead', 'follow_up_date', 'follow_up_type', 'subject', 'completed', 'assigned_to']
    list_filter = ['completed', 'follow_up_type', 'follow_up_date']
    search_fields = ['lead__first_name', 'lead__phone', 'subject', 'notes']


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ['lead', 'visit_date', 'status', 'assigned_staff', 'site_address']
    list_filter = ['status', 'visit_date']
    search_fields = ['lead__first_name', 'site_address', 'requirements']


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ['estimate_number', 'lead', 'estimate_date', 'total_amount', 'status']
    list_filter = ['status', 'estimate_date']
    search_fields = ['estimate_number', 'lead__first_name', 'description']


@admin.register(LeadNote)
class LeadNoteAdmin(admin.ModelAdmin):
    list_display = ['lead', 'created_by', 'created_at']
    search_fields = ['lead__first_name', 'note']


@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ['lead', 'activity_type', 'title', 'performed_by', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['lead__first_name', 'title', 'description']
