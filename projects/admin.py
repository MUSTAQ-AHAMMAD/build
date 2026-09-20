from django.contrib import admin
from .models import (
    ProjectCategory, Project, ProjectTask, ProjectDocument,
    SupportTicket, SupportTicketMessage
)

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}

class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 1

class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'location', 'project_status', 'contract_amount', 'paid_amount', 'progress_percentage', 'published')
    list_filter = ('category', 'project_status', 'featured', 'published')
    search_fields = ('title', 'location', 'overview', 'scope_of_work', 'customer_name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectTaskInline, ProjectDocumentInline]

@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ('project', 'task_name', 'category', 'assigned_to', 'due_date', 'status', 'priority')
    list_filter = ('category', 'status', 'priority')
    search_fields = ('task_name', 'project__title')

@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'document_type', 'visibility', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'visibility')
    search_fields = ('title', 'project__title')

class SupportTicketMessageInline(admin.TabularInline):
    model = SupportTicketMessage
    extra = 1

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'customer_name', 'subject', 'category', 'priority', 'status', 'assigned_to', 'created_at')
    list_filter = ('category', 'priority', 'status')
    search_fields = ('ticket_id', 'customer_name', 'customer_phone', 'subject')
    readonly_fields = ('ticket_id', 'created_at', 'updated_at')
    inlines = [SupportTicketMessageInline]
