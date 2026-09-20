from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Public Blog URLs
    path('blog/', views.public_blog_list, name='public_list'),
    path('blog/dashboard/', views.cms_blog_dashboard, name='workspace_dashboard'),
    path('blog/create/', views.cms_blog_create, name='workspace_create'),
    path('blog/<slug:slug>/', views.public_blog_detail, name='public_detail'),

    # CMS Blog URLs (Matching Section 20 Requirements)
    path('cms/blog/', views.cms_blog_dashboard, name='cms_dashboard'),
    path('cms/blog/dashboard/', views.cms_blog_dashboard, name='cms_dashboard_alias'),
    path('cms/blog/list/', views.cms_blog_list, name='cms_list'),
    path('cms/blog/create/', views.cms_blog_create, name='cms_create'),
    path('cms/blog/<int:pk>/', views.cms_blog_detail, name='cms_detail'),
    path('cms/blog/<int:pk>/edit/', views.cms_blog_edit, name='cms_edit'),
    path('cms/blog/<int:pk>/delete/', views.cms_blog_delete, name='cms_delete'),
    path('cms/blog/<int:pk>/clone/', views.cms_blog_clone, name='cms_clone'),
    path('cms/blog/<int:pk>/toggle-publish/', views.cms_blog_toggle_publish, name='cms_toggle_publish'),
    path('cms/blog/<int:pk>/publish/', views.cms_blog_toggle_publish, name='cms_publish'),
    path('cms/blog/<int:pk>/unpublish/', views.cms_blog_toggle_publish, name='cms_unpublish'),

    # CMS Category URLs
    path('cms/blog/categories/', views.cms_category_list, name='cms_category_list'),
    path('cms/blog/categories/create/', views.cms_category_create, name='cms_category_create'),
    path('cms/blog/categories/<int:pk>/edit/', views.cms_category_edit, name='cms_category_edit'),
    path('cms/blog/categories/<int:pk>/delete/', views.cms_category_delete, name='cms_category_delete'),

    # CMS AI Content Assistant AJAX Endpoint
    path('cms/blog/ai-assist/', views.cms_blog_ai_assist, name='cms_ai_assist'),
]
