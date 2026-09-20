from django import forms
from django.contrib.auth.models import User
from .models import Lead, LeadSource, FollowUp, SiteVisit, Estimate, LeadNote

class LeadForm(forms.ModelForm):
    """Comprehensive Lead Create & Edit Form"""
    class Meta:
        model = Lead
        fields = [
            # Customer
            'first_name', 'last_name', 'company_name', 'phone', 'alternate_phone',
            'email', 'whatsapp_number', 'preferred_contact_method', 'customer_type',

            # Project
            'service_category', 'service_type', 'property_type', 'property_location',
            'city', 'area_locality', 'approximate_property_area', 'unit', 'project_description',

            # Commercial
            'estimated_budget', 'budget_range', 'expected_project_value', 'expected_closing_date',

            # CRM
            'lead_source', 'priority', 'assigned_to', 'status', 'next_follow_up_date',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name *'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company or Firm Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210 *'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alternate Phone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'client@example.com'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'}),
            'preferred_contact_method': forms.Select(attrs={'class': 'form-select'}),
            'customer_type': forms.Select(attrs={'class': 'form-select'}),

            'service_category': forms.Select(attrs={'class': 'form-select'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'property_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Plot No, Street / Colony'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City (e.g. Hyderabad, Bangalore)'}),
            'area_locality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Area / Locality (e.g. Banjara Hills)'}),
            'approximate_property_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2,400'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'sq.ft'}),
            'project_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed scope of requirements, structural observations, timeline requirements...'}),

            'estimated_budget': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ₹25 - 30 Lakhs'}),
            'budget_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 20L - 40L'}),
            'expected_project_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pipeline Value in ₹', 'step': '0.01'}),
            'expected_closing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

            'lead_source': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'next_follow_up_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class LeadQuickAssignForm(forms.ModelForm):
    """Fast Staff Assignment Modal Form"""
    class Meta:
        model = Lead
        fields = ['assigned_to', 'priority']
        widgets = {
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }


class LeadMarkWonForm(forms.ModelForm):
    """Mark Lead as Won Form"""
    won_notes = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Contract details, final agreed scope, project commencement date...'}), required=False)

    class Meta:
        model = Lead
        fields = ['final_project_value', 'won_date']
        widgets = {
            'final_project_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Final Project Value in ₹ *', 'step': '0.01'}),
            'won_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class LeadMarkLostForm(forms.ModelForm):
    """Mark Lead as Lost Form"""
    class Meta:
        model = Lead
        fields = ['lost_reason', 'lost_notes']
        widgets = {
            'lost_reason': forms.Select(attrs={'class': 'form-select'}),
            'lost_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detailed explanation of why the lead was lost...'}),
        }


class LeadOnHoldForm(forms.ModelForm):
    """Place Lead On Hold Form"""
    class Meta:
        model = Lead
        fields = ['on_hold_reason', 'next_follow_up_date']
        widgets = {
            'on_hold_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for placing on hold (e.g. awaiting municipal sanctions, client traveling)...'}),
            'next_follow_up_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class FollowUpForm(forms.ModelForm):
    """Follow-up Scheduling & Logging Form"""
    class Meta:
        model = FollowUp
        fields = [
            'follow_up_date', 'follow_up_time', 'follow_up_type',
            'subject', 'notes', 'outcome', 'next_follow_up_date',
            'assigned_to', 'completed',
        ]
        widgets = {
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'follow_up_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'follow_up_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Review BOQ Estimate with Client'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Discussion agenda / notes'}),
            'outcome': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'What was decided during this call / meeting'}),
            'next_follow_up_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SiteVisitForm(forms.ModelForm):
    """Site Visit Scheduling & Technical Inspection Form"""
    class Meta:
        model = SiteVisit
        fields = [
            'site_address', 'visit_date', 'visit_time', 'assigned_staff',
            'site_contact', 'property_type', 'site_condition', 'requirements',
            'measurements', 'notes', 'status',
        ]
        widgets = {
            'site_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complete property site address *'}),
            'visit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'visit_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'assigned_staff': forms.Select(attrs={'class': 'form-select'}),
            'site_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name & Phone of contact at site'}),
            'property_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 25-yr old 3BHK flat / 400 sq.yd plot'}),
            'site_condition': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dampness, structural column status, soil level, crane access...'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Specific architectural/civil changes requested by client'}),
            'measurements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Field measurements: Room dimensions, column spacing, floor height...'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Internal engineering notes'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class EstimateForm(forms.ModelForm):
    """Estimate & Proposal Tracking Form"""
    class Meta:
        model = Estimate
        fields = [
            'estimate_number', 'estimate_date', 'description',
            'estimated_amount', 'tax_amount', 'total_amount',
            'valid_until', 'status', 'notes',
        ]
        widgets = {
            'estimate_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. EST-2026-001 (Auto if empty)'}),
            'estimate_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Turnkey Flat Renovation BOQ Rev-1 *'}),
            'estimated_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Subtotal ₹ *', 'step': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'GST / Tax ₹', 'step': '0.01'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Grand Total ₹', 'step': '0.01'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Estimate notes & payment terms'}),
        }


class LeadNoteForm(forms.ModelForm):
    """Quick Note Form"""
    class Meta:
        model = LeadNote
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter internal discussion notes or updates here...'}),
        }


class LeadSourceForm(forms.ModelForm):
    """Lead Source Form"""
    class Meta:
        model = LeadSource
        fields = ['name', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Source Name (e.g. Instagram Ads)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
