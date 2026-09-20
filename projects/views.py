from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectCategory

def project_list(request):
    category_slug = request.GET.get('category', '').strip()
    projects = Project.objects.filter(published=True).select_related('category')

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(ProjectCategory, slug=category_slug)
        projects = projects.filter(category=selected_category)

    categories = ProjectCategory.objects.all()
    context = {
        'projects': projects,
        'categories': categories,
        'selected_category': selected_category,
    }
    return render(request, 'projects/project_list.html', context)

def project_detail(request, slug):
    project = get_object_or_404(Project.objects.select_related('category'), slug=slug, published=True)
    related_projects = Project.objects.filter(category=project.category, published=True).exclude(pk=project.pk)[:3]
    return render(request, 'projects/project_detail.html', {'project': project, 'related_projects': related_projects})
