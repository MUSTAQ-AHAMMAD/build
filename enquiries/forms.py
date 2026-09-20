from django import forms
from .models import Enquiry

class PublicEnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = [
            'enquiry_type',
            'full_name',
            'phone_number',
            'email',
            'city_location',
            'property_type',
            'approximate_area',
            'message',
            'site_visit_requested',
        ]
        widgets = {
            'enquiry_type': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name *', 'required': 'required'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone / WhatsApp Number *', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address (Optional)'}),
            'city_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City / Area Location *', 'required': 'required'}),
            'property_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 3BHK Flat, Independent House, Old Building'}),
            'approximate_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Approx Area (e.g. 2,000 sq.ft)'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about your project requirements, property condition, or questions *', 'required': 'required'}),
            'site_visit_requested': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'site_visit_check'}),
        }


class CMSEnquiryUpdateForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['status', 'assigned_engineer', 'internal_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_engineer': forms.TextInput(attrs={'class': 'form-control'}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
