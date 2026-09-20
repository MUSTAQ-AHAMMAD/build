import os
from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import BlogPost, BlogCategory

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            'title',
            'slug',
            'category',
            'author',
            'short_description',
            'featured_image',
            'content',
            'status',
            'published_date',
            'featured',
            'related_service_type',
            'seo_title',
            'seo_description',
            'seo_keywords',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g. Complete Flat Renovation Guide for Resale Apartments',
                'id': 'id_title'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control font-monospace',
                'placeholder': 'auto-generated-from-title-if-blank',
                'id': 'id_slug'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'BUILD+ Editorial Team'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Key summary for search engine snippet and card overview (max 500 characters)...'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/webp,image/jpg',
                'id': 'id_featured_image'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control font-monospace',
                'rows': 16,
                'placeholder': 'Write complete blog content with HTML markup (<h3>, <p>, <ul>, <li>, <blockquote>, etc.)...',
                'id': 'id_content'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_status'
            }),
            'published_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_featured'
            }),
            'related_service_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'seo_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank to use blog title automatically'
            }),
            'seo_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Leave blank to use short description automatically'
            }),
            'seo_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'flat renovation, structural repair, apartment remodeling'
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        if not slug and title:
            slug = slugify(title)
        if slug:
            qs = BlogPost.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("This URL slug is already taken by another blog post. Please specify a unique slug.")
        return slug

    def clean_featured_image(self):
        image = self.cleaned_data.get('featured_image')
        if image and hasattr(image, 'size'):
            # Validate size (Max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image file size must not exceed 5MB.")
            # Validate extension
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise ValidationError("Only JPG, JPEG, PNG, and WebP images are permitted.")
        return image


class BlogCategoryForm(forms.ModelForm):
    class Meta:
        model = BlogCategory
        fields = ['name', 'slug', 'description', 'status', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Flat & Apartment Renovation',
                'id': 'id_cat_name'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control font-monospace',
                'placeholder': 'e.g. flat-apartment-renovation',
                'id': 'id_cat_slug'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description for SEO and category index...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        if not slug and name:
            slug = slugify(name)
        if slug:
            qs = BlogCategory.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("A category with this URL slug already exists.")
        return slug


class AIAssistForm(forms.Form):
    TASK_CHOICES = [
        ('generate_draft', 'Generate Complete Blog Draft & Outline'),
        ('generate_seo', 'Generate Optimized SEO Title, Description & Keywords'),
        ('generate_faqs', 'Generate 4-5 High-Value Frequently Asked Questions (FAQs)'),
        ('improve_content', 'Improve Tone & Structure for Commercial Lead Generation'),
    ]

    topic = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. How to inspect and renovate 20-year-old resale flats before moving in'
        })
    )
    category_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Flat & Apartment Renovation'
        })
    )
    task_type = forms.ChoiceField(
        choices=TASK_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    custom_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Optional instructions (e.g. emphasize plumbing, water leakage, and budget estimation)'
        })
    )
