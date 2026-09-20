import random
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User

class ProjectCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = "Project Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning & Permits'),
        ('ready_to_start', 'Ready to Start'),
        ('ongoing', 'Under Execution / In Progress'),
        ('near_completion', 'Near Completion / Finishing'),
        ('completed', 'Completed & Handed Over'),
        ('on_hold', 'On Hold'),
        ('delayed', 'Delayed'),
    ]

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    category = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE, related_name='projects')
    location = models.CharField(max_length=150, default="Jubilee Hills, Hyderabad")
    project_type = models.CharField(max_length=120, default="3BHK Flat Renovation")
    client_type = models.CharField(max_length=100, default="Private Homeowner")
    project_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='completed')
    duration = models.CharField(max_length=50, default="3 Months")
    built_up_area = models.CharField(max_length=50, default="2,400 sq.ft")

    # Commercial & Customer Association
    customer_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_projects')
    customer_name = models.CharField(max_length=150, blank=True)
    customer_phone = models.CharField(max_length=30, blank=True)
    customer_email = models.EmailField(blank=True)
    contract_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, help_text="Total Agreed Project Value in ₹")
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, help_text="Total Cleared Payments in ₹")
    progress_percentage = models.PositiveIntegerField(default=0, help_text="0 to 100%")

    start_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects')

    overview = models.TextField()
    scope_of_work = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    solutions = models.TextField(blank=True)

    main_image = models.ImageField(upload_to='projects/', blank=True, null=True)
    before_image = models.ImageField(upload_to='projects/before/', blank=True, null=True)
    after_image = models.ImageField(upload_to='projects/after/', blank=True, null=True)

    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'slug': self.slug})


class ProjectTask(models.Model):
    """Execution Work Packages & Engineering Task Breakdown"""
    TASK_CATEGORIES = [
        ('site_prep', 'Site Preparation & Clearance'),
        ('demolition', 'Demolition & Dismantling'),
        ('foundation', 'Soil Investigation & Foundation RCC'),
        ('structure', 'RCC Columns, Beams & Slabs'),
        ('brickwork', 'Brickwork & Masonry'),
        ('plumbing_mep', 'Plumbing, Drainage & Sanitary (MEP)'),
        ('electrical', 'Electrical Conduiting & Distribution'),
        ('plastering', 'Internal / External Plastering & Waterproofing'),
        ('flooring', 'Tiling & Flooring'),
        ('painting', 'Putty, Primer & Painting'),
        ('woodwork', 'Doors, Windows & Woodwork'),
        ('inspection', 'Civil & Quality Inspection'),
        ('handover', 'Final Handover & Snag Rectification'),
    ]

    TASK_STATUSES = [
        ('PENDING', 'Pending Initiation'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('BLOCKED', 'Blocked / On Hold'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    task_name = models.CharField(max_length=200)
    category = models.CharField(max_length=40, choices=TASK_CATEGORIES, default='structure')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TASK_STATUSES, default='PENDING')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    progress_percentage = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['project', 'display_order', 'due_date']
        verbose_name = "Project Task"
        verbose_name_plural = "Project Tasks"

    def __str__(self):
        return f"{self.project.title} - {self.task_name} [{self.status}]"


class ProjectDocument(models.Model):
    """Centralized Document Storage (Contracts, Drawings, Municipal NOCs, Inspection Reports)"""
    DOC_TYPES = [
        ('contract', 'Signed Contract / Agreement'),
        ('drawing', 'Architectural / Structural 2D/3D Drawing'),
        ('approval', 'Municipal Building Permit / Sanction / NOC'),
        ('boq', 'Detailed Bill of Quantities (BOQ)'),
        ('report', 'Site Audit / Soil Investigation Report'),
        ('material_test', 'Concrete Cube / Steel Quality Test Certificate'),
        ('invoice', 'Commercial Tax Invoice'),
        ('handover', 'Handover Certificate & Snag Checklist'),
        ('other', 'Other Document'),
    ]

    VISIBILITY_CHOICES = [
        ('ADMIN_ONLY', 'Admin & Superuser Only'),
        ('STAFF', 'Internal Staff & Engineers'),
        ('CUSTOMER', 'Shared with Customer in Portal'),
        ('PUBLIC', 'Publicly Accessible'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOC_TYPES, default='other')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='projects/documents/%Y/%m/')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='CUSTOMER')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Project Document"
        verbose_name_plural = "Project Documents"

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"


class SupportTicket(models.Model):
    """Customer Support & Issue Ticketing Desk"""
    CATEGORY_CHOICES = [
        ('project_progress', 'Project Execution / Progress Query'),
        ('billing_payment', 'Billing, Milestone & Payment Query'),
        ('site_inspection', 'Site Visit / Inspection Request'),
        ('quality_materials', 'Material Quality & Specifications'),
        ('general_inquiry', 'General Service Request'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open / New'),
        ('IN_PROGRESS', 'In Progress / Assigned'),
        ('WAITING_FOR_CUSTOMER', 'Waiting for Customer Response'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    ticket_id = models.CharField(max_length=40, unique=True, editable=False, db_index=True)
    customer_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='support_tickets')
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=30)
    customer_email = models.EmailField(blank=True)

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='support_tickets')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='project_progress')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    subject = models.CharField(max_length=255)
    description = models.TextField()

    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='OPEN', db_index=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_support_tickets')
    resolution_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Support Ticket"
        verbose_name_plural = "Support Tickets"

    def __str__(self):
        return f"{self.ticket_id} - {self.subject} [{self.status}]"

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            year_str = timezone.now().strftime('%Y')
            random_int = random.randint(100000, 999999)
            self.ticket_id = f"TCK-{year_str}-{random_int}"
            while SupportTicket.objects.filter(ticket_id=self.ticket_id).exists():
                random_int = random.randint(100000, 999999)
                self.ticket_id = f"TCK-{year_str}-{random_int}"
        super().save(*args, **kwargs)


class SupportTicketMessage(models.Model):
    """Threaded Discussion / Support Messages on a Ticket"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sender_name = models.CharField(max_length=150)
    message = models.TextField()
    attachment = models.FileField(upload_to='support/attachments/%Y/%m/', blank=True, null=True)
    is_staff_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Ticket Message"
        verbose_name_plural = "Ticket Messages"

    def __str__(self):
        return f"Message by {self.sender_name} on {self.ticket.ticket_id}"
