from django.contrib import admin
from .models import BlogCategory, BlogPost

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status', 'display_order', 'created_at', 'total_blogs_count')
    list_filter = ('status',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'featured', 'related_service_type', 'published_date')
    list_filter = ('status', 'featured', 'category', 'related_service_type', 'published_date')
    search_fields = ('title', 'short_description', 'content', 'author')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    ordering = ('-published_date', '-created_at')
