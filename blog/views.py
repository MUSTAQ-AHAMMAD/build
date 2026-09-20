from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import BlogPost, BlogCategory
from .forms import BlogPostForm, BlogCategoryForm, AIAssistForm
from .gemini_helper import call_gemini_ai_assistant

def staff_required(view_func):
    """Decorator ensuring user is logged in and is staff/admin"""
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_staff, login_url='/cms/login/')(view_func))
    return decorated_view_func


# ==============================================================================
# PUBLIC BLOG VIEWS
# ==============================================================================

def public_blog_list(request):
    """
    Public Blog & Knowledge Centre list view with search, category filtering,
    featured post spotlight, and pagination.
    """
    category_slug = request.GET.get('category', '').strip()
    search_query = request.GET.get('q', '').strip()

    # Public users only see published blogs
    blog_qs = BlogPost.objects.filter(status='published').select_related('category')

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(BlogCategory, slug=category_slug, status='active')
        blog_qs = blog_qs.filter(category=selected_category)

    if search_query:
        blog_qs = blog_qs.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Featured blog for hero spotlight (if no search or specific filter)
    featured_blog = None
    if not search_query and not category_slug:
        featured_blog = blog_qs.filter(featured=True).first()
        if not featured_blog:
            featured_blog = blog_qs.first()

    # Exclude hero spotlight from the main grid if present on page 1
    page = request.GET.get('page', 1)
    grid_blogs = blog_qs
    if featured_blog and str(page) == '1' and not search_query and not category_slug:
        grid_blogs = grid_blogs.exclude(pk=featured_blog.pk)

    paginator = Paginator(grid_blogs, 9)  # 3x3 responsive grid
    try:
        blogs_page = paginator.page(page)
    except PageNotAnInteger:
        blogs_page = paginator.page(1)
    except EmptyPage:
        blogs_page = paginator.page(paginator.num_pages)

    # Active categories with published counts
    categories = BlogCategory.objects.filter(status='active').annotate(
        pub_count=Count('blogs', filter=Q(blogs__status='published'))
    ).filter(pub_count__gt=0)

    context = {
        'blogs': blogs_page,
        'featured_blog': featured_blog,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'total_published': blog_qs.count(),
    }
    return render(request, 'blog/public_list.html', context)


def public_blog_detail(request, slug):
    """
    Public Single Blog Post Detail view with rich content, author info,
    reading time, dynamic commercial lead CTA, and related blogs.
    """
    blog = get_object_or_404(
        BlogPost.objects.select_related('category'),
        slug=slug,
        status='published'
    )

    # Related blogs: same category first, fallback to latest published (exclude current)
    related_blogs = BlogPost.objects.filter(
        category=blog.category,
        status='published'
    ).exclude(pk=blog.pk)[:3]

    if related_blogs.count() < 3:
        needed = 3 - related_blogs.count()
        existing_ids = [blog.pk] + [b.pk for b in related_blogs]
        fallback_blogs = BlogPost.objects.filter(
            status='published'
        ).exclude(pk__in=existing_ids)[:needed]
        related_blogs = list(related_blogs) + list(fallback_blogs)

    context = {
        'blog': blog,
        'related_blogs': related_blogs,
    }
    return render(request, 'blog/public_detail.html', context)


# ==============================================================================
# CMS BLOG MANAGEMENT VIEWS (STAFF / ADMIN ONLY)
# ==============================================================================

@staff_required
def cms_blog_dashboard(request):
    """CMS Blog Overview Dashboard with statistics and recent activity."""
    total_blogs = BlogPost.objects.count()
    published_blogs = BlogPost.objects.filter(status='published').count()
    draft_blogs = BlogPost.objects.filter(status='draft').count()
    featured_blogs = BlogPost.objects.filter(featured=True).count()
    total_categories = BlogCategory.objects.count()

    recent_blogs = BlogPost.objects.select_related('category').order_by('-created_at')[:8]
    recent_categories = BlogCategory.objects.annotate(
        blog_count=Count('blogs')
    ).order_by('-created_at')[:6]

    context = {
        'total_blogs': total_blogs,
        'published_blogs': published_blogs,
        'draft_blogs': draft_blogs,
        'featured_blogs': featured_blogs,
        'total_categories': total_categories,
        'recent_blogs': recent_blogs,
        'recent_categories': recent_categories,
        'ai_form': AIAssistForm(),
    }
    return render(request, 'cms_blog/dashboard.html', context)


@staff_required
def cms_blog_list(request):
    """
    CMS Blog List Table with Search, Category Filter, Status Filter,
    Pagination, and Quick Actions.
    """
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    category_id = request.GET.get('category', '').strip()

    blog_qs = BlogPost.objects.select_related('category').all()

    if search_query:
        blog_qs = blog_qs.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    if status_filter in ['draft', 'published']:
        blog_qs = blog_qs.filter(status=status_filter)

    if category_id:
        blog_qs = blog_qs.filter(category_id=category_id)

    paginator = Paginator(blog_qs, 10)  # 10 blogs per page as requested
    page = request.GET.get('page', 1)
    try:
        blogs_page = paginator.page(page)
    except PageNotAnInteger:
        blogs_page = paginator.page(1)
    except EmptyPage:
        blogs_page = paginator.page(paginator.num_pages)

    categories = BlogCategory.objects.all()

    context = {
        'blogs': blogs_page,
        'categories': categories,
        'search_query': search_query,
        'status_filter': status_filter,
        'selected_category_id': category_id,
        'total_count': blog_qs.count(),
        'published_count': BlogPost.objects.filter(status='published').count(),
        'draft_count': BlogPost.objects.filter(status='draft').count(),
    }
    return render(request, 'cms_blog/list.html', context)


@staff_required
def cms_blog_create(request):
    """Create new Blog Post with validation, auto-slug, and Draft/Publish actions."""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            
            # Action button handling
            action = request.POST.get('action', 'save_draft')
            if action == 'publish':
                blog.status = 'published'
                if not blog.published_date:
                    blog.published_date = timezone.now()
            elif action == 'save_draft':
                blog.status = 'draft'

            blog.save()
            messages.success(request, f"Blog post '{blog.title}' created successfully as {blog.get_status_display()}!")
            return redirect('blog:cms_list')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = BlogPostForm(initial={
            'author': request.user.get_full_name() or request.user.username or 'BUILD+ Editorial Team',
            'status': 'draft',
            'published_date': timezone.now().strftime('%Y-%m-%dT%H:%M')
        })

    context = {
        'form': form,
        'is_edit': False,
        'ai_form': AIAssistForm(),
    }
    return render(request, 'cms_blog/create.html', context)


@staff_required
def cms_blog_edit(request, pk):
    """Edit existing Blog Post."""
    blog = get_object_or_404(BlogPost, pk=pk)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            updated_blog = form.save(commit=False)
            
            action = request.POST.get('action')
            if action == 'publish':
                updated_blog.status = 'published'
                if not updated_blog.published_date:
                    updated_blog.published_date = timezone.now()
            elif action == 'save_draft':
                updated_blog.status = 'draft'

            updated_blog.save()
            messages.success(request, f"Blog post '{updated_blog.title}' updated successfully!")
            return redirect('blog:cms_detail', pk=updated_blog.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = BlogPostForm(instance=blog)

    context = {
        'form': form,
        'blog': blog,
        'is_edit': True,
        'ai_form': AIAssistForm(),
    }
    return render(request, 'cms_blog/edit.html', context)


@staff_required
def cms_blog_detail(request, pk):
    """CMS preview of a blog post with full metadata and action buttons."""
    blog = get_object_or_404(BlogPost.objects.select_related('category'), pk=pk)
    context = {
        'blog': blog,
    }
    return render(request, 'cms_blog/detail.html', context)


@staff_required
def cms_blog_delete(request, pk):
    """Delete blog post with confirmation page and POST-only execution."""
    blog = get_object_or_404(BlogPost, pk=pk)

    if request.method == 'POST':
        title = blog.title
        blog.delete()
        messages.success(request, f"Blog post '{title}' deleted successfully.")
        return redirect('blog:cms_list')

    context = {
        'blog': blog,
    }
    return render(request, 'cms_blog/delete.html', context)


@staff_required
@require_POST
def cms_blog_toggle_publish(request, pk):
    """Toggle blog status between Draft and Published."""
    blog = get_object_or_404(BlogPost, pk=pk)
    if blog.status == 'published':
        blog.status = 'draft'
        messages.info(request, f"Blog post '{blog.title}' unpublished and moved to Drafts.")
    else:
        blog.status = 'published'
        if not blog.published_date:
            blog.published_date = timezone.now()
        messages.success(request, f"Blog post '{blog.title}' is now Published and live on the website!")
    
    blog.save()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'blog:cms_list'
    return redirect(next_url)


@staff_required
@require_POST
def cms_blog_clone(request, pk):
    """Duplicate an existing blog post as a new draft."""
    original = get_object_or_404(BlogPost, pk=pk)
    new_title = f"Copy of {original.title}"
    counter = 1
    while BlogPost.objects.filter(title=new_title).exists():
        counter += 1
        new_title = f"Copy ({counter}) of {original.title}"

    cloned_blog = BlogPost.objects.create(
        title=new_title,
        category=original.category,
        author=original.author,
        short_description=original.short_description,
        content=original.content,
        status='draft',
        featured=False,
        related_service_type=original.related_service_type,
        seo_title=original.seo_title,
        seo_description=original.seo_description,
        seo_keywords=original.seo_keywords,
    )
    messages.success(request, f"Blog post duplicated as draft: '{cloned_blog.title}'")
    return redirect('blog:cms_edit', pk=cloned_blog.pk)


# ==============================================================================
# CATEGORY MANAGEMENT VIEWS
# ==============================================================================

@staff_required
def cms_category_list(request):
    """List all categories with blog counts and management options."""
    categories = BlogCategory.objects.annotate(
        total_blogs=Count('blogs'),
        pub_blogs=Count('blogs', filter=Q(blogs__status='published'))
    ).order_by('display_order', 'name')

    context = {
        'categories': categories,
    }
    return render(request, 'cms_blog/categories.html', context)


@staff_required
def cms_category_create(request):
    """Create new Blog Category."""
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Category '{cat.name}' created successfully!")
            return redirect('blog:cms_category_list')
        else:
            messages.error(request, "Error creating category. Please review form fields.")
    else:
        form = BlogCategoryForm()

    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'cms_blog/category_create.html', context)


@staff_required
def cms_category_edit(request, pk):
    """Edit existing Blog Category."""
    cat = get_object_or_404(BlogCategory, pk=pk)

    if request.method == 'POST':
        form = BlogCategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{cat.name}' updated successfully!")
            return redirect('blog:cms_category_list')
        else:
            messages.error(request, "Error updating category.")
    else:
        form = BlogCategoryForm(instance=cat)

    context = {
        'form': form,
        'category': cat,
        'is_edit': True,
    }
    return render(request, 'cms_blog/category_edit.html', context)


@staff_required
def cms_category_delete(request, pk):
    """Safe category deletion with protection against deleting categories with blogs."""
    cat = get_object_or_404(BlogCategory, pk=pk)
    blog_count = cat.blogs.count()

    if request.method == 'POST':
        if blog_count > 0:
            messages.error(
                request,
                f"Cannot delete category '{cat.name}' because it contains {blog_count} blog post(s). "
                f"Please reassign or delete the associated blog posts first."
            )
            return redirect('blog:cms_category_list')
        
        name = cat.name
        cat.delete()
        messages.success(request, f"Category '{name}' deleted successfully.")
        return redirect('blog:cms_category_list')

    context = {
        'category': cat,
        'blog_count': blog_count,
    }
    return render(request, 'cms_blog/category_delete.html', context)


# ==============================================================================
# AI ASSIST AJAX ENDPOINT
# ==============================================================================

@staff_required
@require_POST
def cms_blog_ai_assist(request):
    """AJAX endpoint for Google AI Studio / Gemini content generation."""
    topic = request.POST.get('topic', '').strip()
    task_type = request.POST.get('task_type', 'generate_draft')
    category_name = request.POST.get('category_name', '')
    custom_instructions = request.POST.get('custom_instructions', '')

    if not topic:
        return JsonResponse({'success': False, 'error': 'Topic is required.'}, status=400)

    result = call_gemini_ai_assistant(
        topic=topic,
        task_type=task_type,
        category_name=category_name,
        custom_instructions=custom_instructions
    )
    return JsonResponse(result)
